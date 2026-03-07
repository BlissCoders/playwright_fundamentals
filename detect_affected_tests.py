#!/usr/bin/env python3
"""
Detect affected tests based on actual code dependencies and imports.

This script analyzes which individual test functions/methods are affected by 
changes in source files by examining import chains and file dependencies. 
It also detects when configuration files change and triggers full test suite runs.
"""
import subprocess
import sys
import ast
import os
from pathlib import Path
from typing import Set, List, Dict, Tuple


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


def extract_test_functions(test_file: str) -> Dict[str, List[str]]:
    """
    Extract test functions and their imported/used symbols from a test file.
    Returns dict: {test_name: [symbols_used]}
    """
    test_functions = {}
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        # Extract class methods and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Get all names referenced in this function
                symbols = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        symbols.add(child.id)
                test_functions[node.name] = list(symbols)
            
            elif isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                # Extract test methods from test classes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        symbols = set()
                        for child in ast.walk(item):
                            if isinstance(child, ast.Name):
                                symbols.add(child.id)
                        test_methods = f"{node.name}::{item.name}"
                        test_functions[test_methods] = list(symbols)
    
    except Exception as e:
        print(f"Warning: Could not parse test file {test_file}: {e}", file=sys.stderr)
    
    return test_functions


def extract_functions_and_classes(source_file: str) -> Dict[str, Set[str]]:
    """
    Extract function/class definitions and what they import/use.
    Returns dict: {function_name: {imports_used}}
    """
    definitions = {}
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                symbols = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        symbols.add(child.id)
                definitions[node.name] = symbols
    
    except Exception as e:
        print(f"Warning: Could not parse {source_file}: {e}", file=sys.stderr)
    
    return definitions


def find_affected_tests(changed_files: Set[str]) -> Set[str]:
    """
    Find individual test functions/methods affected by changed source files.
    Returns pytest node IDs for specific tests.
    
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
        return {"tests"}  # Run entire tests directory
    
    # Build map of source files and their exports/definitions
    source_definitions = {}
    for py_file in Path(".").rglob("*.py"):
        if "tests" not in str(py_file) and ".venv" not in str(py_file) and ".git" not in str(py_file):
            try:
                file_str = str(py_file)
                source_definitions[file_str] = {
                    'imports': extract_imports(file_str),
                    'definitions': extract_functions_and_classes(file_str)
                }
            except Exception as e:
                print(f"Warning: Could not process {py_file}: {e}", file=sys.stderr)
    
    # Analyze each test file
    for test_file in tests_dir.rglob("test_*.py"):
        test_file_str = str(test_file)
        test_functions = extract_test_functions(test_file_str)
        test_imports = extract_imports(test_file_str)
        
        print(f"Analyzing {test_file_str}", file=sys.stderr)
        print(f"  Test functions found: {list(test_functions.keys())}", file=sys.stderr)
        
        # Check each test function
        for test_name, test_symbols in test_functions.items():
            affected = False
            
            # Check each changed file
            for changed_file in changed_files:
                if changed_file.endswith('.py') and not changed_file.startswith('tests/'):
                    changed_module = get_source_module_name(changed_file)
                    changed_file_str = str(Path(changed_file))
                    
                    # Direct import: test imports the changed module
                    if any(imp in changed_module or changed_module in imp for imp in test_imports):
                        affected = True
                        print(f"  ✓ {test_name} affected (imports changed module {changed_module})", file=sys.stderr)
                        break
                    
                    # Check if test uses functions/classes from the changed file
                    if changed_file_str in source_definitions:
                        source_defs = source_definitions[changed_file_str]['definitions']
                        
                        # If test uses any function/class from changed file
                        if any(sym in test_symbols for sym in source_defs.keys()):
                            affected = True
                            print(f"  ✓ {test_name} affected (uses changed functions: {set(test_symbols) & set(source_defs.keys())})", file=sys.stderr)
                            break
                    
                    # Check transitive dependencies
                    for source_file_str, source_info in source_definitions.items():
                        source_imports = source_info['imports']
                        source_defs = source_info['definitions']
                        
                        # If changed file is imported by this source module
                        if any(imp in changed_module for imp in source_imports) or changed_file == source_file_str:
                            # If test uses something from this source module
                            if any(sym in test_symbols for sym in source_defs.keys()):
                                affected = True
                                print(f"  ✓ {test_name} affected (transitively depends on {changed_file})", file=sys.stderr)
                                break
                    
                    if affected:
                        break
            
            if affected:
                # Format as pytest node ID for specific test
                if "::" in test_name:
                    # Test method in class
                    affected_tests.add(f"{test_file_str}::{test_name}")
                else:
                    # Standalone test function
                    affected_tests.add(f"{test_file_str}::{test_name}")
    
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
    
    if affected and affected != {"tests"}:
        print(f"\nFound {len(affected)} affected test(s)", file=sys.stderr)
        for test in sorted(affected):
            print(f"  - {test}", file=sys.stderr)
        # Output as space-separated pytest node IDs
        print(" ".join(sorted(affected)))
    elif affected == {"tests"}:
        print("Running full test suite", file=sys.stderr)
        print("tests")
    else:
        print("No affected tests found, running full test suite as fallback", file=sys.stderr)
        print("tests")


if __name__ == "__main__":
    main()