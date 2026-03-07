#!/usr/bin/env python3
"""
Detect affected tests based on actual code dependencies and imports.

This script analyzes which test files are affected by changes in source files
by examining import chains and file dependencies. It also detects when
configuration files change and triggers full test suite runs.
"""
import subprocess
import sys
import ast
import os
from pathlib import Path
from typing import Set

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
            print(f"Changed files: {changed}", file=sys.stderr)
        return changed
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not detect changed files: {e}", file=sys.stderr)
        print("Running all tests as fallback", file=sys.stderr)
        return set()

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

def find_affected_tests(changed_files: Set[str]) -> Set[str]:
    """
    Find test files affected by changed source files.
    
    Configuration files that trigger full test suite:
    - requirements.txt (Python dependencies)
    - pom.xml (Maven dependencies)
    - setup.py (Python package setup)
    - pyproject.toml (Python project config)
    """
    affected_tests = set()
    tests_dir = Path("tests")
    
    # Check if configuration files were changed
    config_files = {'requirements.txt', 'pom.xml', 'setup.py', 'pyproject.toml', 'conftest.py'}
    if any(changed_file in config_files for changed_file in changed_files):
        print("Configuration files changed, running all tests", file=sys.stderr)
        affected_tests = set(tests_dir.rglob("test_*.py"))
        return affected_tests
    
    # Map of source modules to their dependencies
    source_modules = {}
    for py_file in Path(".").rglob("*.py"):
        if "tests" not in str(py_file) and ".venv" not in str(py_file) and ".git" not in str(py_file):
            try:
                module_name = get_source_module_name(str(py_file))
                source_modules[str(py_file)] = extract_imports(str(py_file))
            except Exception as e:
                print(f"Warning: Could not process {py_file}: {e}", file=sys.stderr)
    
    # Check each test file
    for test_file in tests_dir.rglob("test_*.py"):
        test_imports = extract_imports(str(test_file))
        
        # Check if any changed file is imported by this test
        for changed_file in changed_files:
            if changed_file.endswith('.py') and not changed_file.startswith('tests/'): 
                changed_module = get_source_module_name(changed_file)
                
                # Direct import: test imports the changed module
                for imp in test_imports:
                    if imp in changed_module or changed_module in imp:
                        affected_tests.add(str(test_file))
                        print(f"Test {test_file} imports {changed_file}", file=sys.stderr)
                        break
                
                if str(test_file) in affected_tests:
                    break
                
                # Check transitive dependencies: 
                # if changed file is imported by something the test imports
                for source_file, source_imports in source_modules.items():
                    source_module = get_source_module_name(source_file)
                    
                    # If changed file is imported by this source module
                    if any(imp in changed_module for imp in source_imports) or changed_file == source_file:
                        # If test imports this source module
                        if any(imp in source_module for imp in test_imports):
                            affected_tests.add(str(test_file))
                            print(f"Test {test_file} transitively depends on {changed_file}", file=sys.stderr)
                            break
    
    return affected_tests

def main():
    """Main entry point."""
    base_branch = sys.argv[1] if len(sys.argv) > 1 else "origin/master"
    
    print(f"Detecting affected tests (base: {base_branch})", file=sys.stderr)
    
    changed_files = get_changed_files(base_branch)
    
    if not changed_files:
        print("No changes detected, running all tests", file=sys.stderr)
        print("tests")
        return
    
    affected = find_affected_tests(changed_files)
    
    if affected:
        print(f"Found {len(affected)} affected test file(s)", file=sys.stderr)
        print(" ".join(sorted(affected)))
    else:
        print("No affected tests found, running full test suite as fallback", file=sys.stderr)
        print("tests")


if __name__ == "__main__":
    main()