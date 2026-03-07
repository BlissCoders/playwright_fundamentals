#!/usr/bin/env python3
"""
Detect affected test FUNCTIONS based on actual code changes.

This script analyzes which specific test functions are affected by changes
in source files by examining:
1. Direct changes to test functions
2. Changes to source code that tests depend on
3. Changes to configuration files (triggers full suite)

It returns pytest node IDs like: tests/test_file.py::TestClass::test_method
"""
import subprocess
import sys
import ast
import os
from pathlib import Path
from typing import Set, Dict, List, Tuple


def get_changed_files(base_branch: str = "origin/master") -> Set[str]:
    """Get files changed in current branch vs base branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_branch + "...HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        changed = set(result.stdout.strip().split('\n')) - {''}
        if changed:
            print(f"Changed files detected: {changed}", file=sys.stderr)
        return changed
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not detect changed files: {e}", file=sys.stderr)
        return set()


def get_changed_line_ranges(file_path: str, base_branch: str) -> List[Tuple[int, int]]:
    """Get line ranges that were changed in a file using git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "-U0", base_branch + "...HEAD", "--", file_path],
            capture_output=True,
            text=True,
            check=False
        )

        line_ranges = []
        lines = result.stdout.split('\n')

        for line in lines:
            if line.startswith('@@'):
                # Extract line number from @@ -old_line,count +new_line,count @@
                parts = line.split(' ')
                if len(parts) >= 3:
                    new_range = parts[2]  # +new_line,count or +new_line
                    try:
                        new_line_str = new_range.lstrip('+')
                        if ',' in new_line_str:
                            start_line, count = new_line_str.split(',')
                            start_line = int(start_line)
                            count = int(count)
                        else:
                            start_line = int(new_line_str)
                            count = 1

                        line_ranges.append((start_line, start_line + count))
                    except ValueError:
                        pass

        return line_ranges
    except Exception as e:
        print(f"Warning: Could not get changed lines in {file_path}: {e}", file=sys.stderr)
        return []


def extract_test_structure(file_path: str) -> Dict[str, Dict]:
    """
    Extract test classes and their methods with line numbers.

    Returns:
        Dict mapping class names to dict of {'methods': {method_name: line_number}}
        Example: {'TestLogin': {'methods': {'test_login_success': 10, 'test_login_failure': 15}}}
    """
    test_structure = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Found a test class
                class_name = node.name
                methods = {}

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Check if it's a test method
                        if item.name.startswith('test_'):
                            methods[item.name] = item.lineno

                if methods:
                    test_structure[class_name] = {
                        'lineno': node.lineno,
                        'methods': methods
                    }

            # Also check for standalone test functions
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    if '__standalone__' not in test_structure:
                        test_structure['__standalone__'] = {'methods': {}}
                    test_structure['__standalone__']['methods'][node.name] = node.lineno

    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)

    return test_structure


def extract_imports(file_path: str) -> Set[str]:
    """Extract all top-level imports from a Python file."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)

    return imports


def get_source_module_name(file_path: str) -> str:
    """Convert file path to module name."""
    return Path(file_path).with_suffix('').as_posix().replace('/', '.')


def find_functions_in_line_range(test_structure: Dict[str, Dict], start_line: int, end_line: int) -> List[
    Tuple[str, str]]:
    """
    Find test functions that fall within the changed line range.

    Returns:
        List of tuples: [(class_name, method_name), ...]
    """
    affected = []

    for class_name, class_info in test_structure.items():
        if class_name == '__standalone__':
            # Standalone functions
            for method_name, lineno in class_info['methods'].items():
                if start_line <= lineno < end_line:
                    affected.append(('', method_name))
        else:
            # Methods in class
            for method_name, lineno in class_info['methods'].items():
                if start_line <= lineno < end_line:
                    affected.append((class_name, method_name))

    return affected


def find_affected_test_nodeids(changed_files: Set[str], base_branch: str = "origin/master") -> List[str]:
    """
    Find specific test function node IDs affected by changes.

    Configuration files that trigger full test suite:
    - requirements.txt
    - pom.xml
    - setup.py
    - pyproject.toml
    - conftest.py
    """
    affected_nodeids = set()
    tests_dir = Path("tests")

    # Check if configuration files were changed
    config_files = {'requirements.txt', 'pom.xml', 'setup.py', 'pyproject.toml', 'conftest.py'}
    if any(changed_file in config_files for changed_file in changed_files):
        print("Configuration files changed, running full test suite", file=sys.stderr)
        return ["tests"]  # Signal to run all tests

    # Build map of source modules to their dependencies
    source_modules = {}
    for py_file in Path(".").rglob("*.py"):
        path_str = str(py_file)
        if "tests" not in path_str and ".venv" not in path_str and ".git" not in path_str:
            try:
                module_name = get_source_module_name(path_str)
                source_modules[path_str] = extract_imports(path_str)
            except Exception:
                pass

    # Process direct test file changes
    for changed_file in changed_files:
        if changed_file.startswith('tests/') and changed_file.endswith('.py'):
            # Test file was directly changed
            print(f"Test file changed: {changed_file}", file=sys.stderr)

            # Get line ranges that were changed
            line_ranges = get_changed_line_ranges(changed_file, base_branch)

            if line_ranges:
                # Get test structure
                test_structure = extract_test_structure(changed_file)

                # Find affected functions in changed line ranges
                for start, end in line_ranges:
                    affected_funcs = find_functions_in_line_range(test_structure, start, end)

                    for class_name, method_name in affected_funcs:
                        if class_name:
                            nodeid = f"{changed_file}::{class_name}::{method_name}"
                        else:
                            nodeid = f"{changed_file}::{method_name}"
                        affected_nodeids.add(nodeid)
                        print(f"Found affected test: {nodeid}", file=sys.stderr)
            else:
                # If we can't determine specific functions, add all tests in file
                print(f"Could not determine specific changes, adding all tests from {changed_file}", file=sys.stderr)
                test_structure = extract_test_structure(changed_file)
                for class_name, class_info in test_structure.items():
                    for method_name in class_info['methods']:
                        if class_name != '__standalone__':
                            nodeid = f"{changed_file}::{class_name}::{method_name}"
                        else:
                            nodeid = f"{changed_file}::{method_name}"
                        affected_nodeids.add(nodeid)

        elif changed_file.endswith('.py') and not changed_file.startswith('tests/'):
            # Source file was changed - find which tests depend on it
            print(f"Source file changed: {changed_file}", file=sys.stderr)
            changed_module = get_source_module_name(changed_file)

            # Check each test file for dependencies
            for test_file in tests_dir.rglob("test_*.py"):
                test_imports = extract_imports(str(test_file))
                test_structure = extract_test_structure(str(test_file))

                # Check if this test imports the changed module
                module_matches = any(
                    imp in changed_module or changed_module in imp
                    for imp in test_imports
                )

                if module_matches:
                    print(f"Test {test_file} imports changed module {changed_file}", file=sys.stderr)

                    # Add only the specific test functions that directly use the changed module
                    for class_name, class_info in test_structure.items():
                        for method_name in class_info['methods']:
                            if class_name != '__standalone__':
                                nodeid = f"{test_file}::{class_name}::{method_name}"
                            else:
                                nodeid = f"{test_file}::{method_name}"
                            affected_nodeids.add(nodeid)

                # Check transitive dependencies
                for source_file, source_imports in source_modules.items():
                    source_module = get_source_module_name(source_file)

                    if any(imp in changed_module for imp in source_imports) or changed_file == source_file:
                        if any(imp in source_module for imp in test_imports) or source_module in changed_module:
                            print(f"Test {test_file} transitively depends on {changed_file}", file=sys.stderr)

                            for class_name, class_info in test_structure.items():
                                for method_name in class_info['methods']:
                                    if class_name != '__standalone__':
                                        nodeid = f"{test_file}::{class_name}::{method_name}"
                                    else:
                                        nodeid = f"{test_file}::{method_name}"
                                    affected_nodeids.add(nodeid)

    return sorted(list(affected_nodeids))


def main():
    """Main entry point."""
    base_branch = sys.argv[1] if len(sys.argv) > 1 else "origin/master"

    print(f"Detecting affected test functions (base: {base_branch})", file=sys.stderr)

    changed_files = get_changed_files(base_branch)

    if not changed_files:
        print("No changes detected", file=sys.stderr)
        print("tests")  # Run all tests as default
        return

    affected_nodeids = find_affected_test_nodeids(changed_files, base_branch)

    if affected_nodeids:
        if affected_nodeids == ["tests"]:
            print("Running full test suite", file=sys.stderr)
            print("tests")
        else:
            print(f"Found {len(affected_nodeids)} affected test function(s)", file=sys.stderr)
            for nodeid in affected_nodeids:
                print(f"  - {nodeid}", file=sys.stderr)
            print(" ".join(affected_nodeids))
    else:
        print("No affected tests found, running full suite as fallback", file=sys.stderr)
        print("tests")


if __name__ == "__main__":
    main()