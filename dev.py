#!/usr/bin/env python3
"""
Development task runner script.

This file is part of sigrok-dev-tools.
Copyright (C) 2025 Oleksandr Kolodkin <oleksandr.kolodkin@ukr.net>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=True if isinstance(cmd, str) else False)
    if result.returncode != 0:
        print(f"❌ {description} failed!")
        return False
    print(f"✅ {description} completed successfully!")
    return True


def test():
    """Run all tests."""
    return run_command(['poetry', 'run', 'pytest', '-v'], "Running tests")


def test_coverage():
    """Run tests with coverage report."""
    return run_command([
        'poetry', 'run', 'pytest', '-v', 
        '--cov=src/sigrok_dev', '--cov-report=html', '--cov-report=term-missing'
    ], "Running tests with coverage")


def lint():
    """Run linting checks."""
    success = True
    success &= run_command(['poetry', 'run', 'black', '--check', 'src', 'tests'], "Checking code formatting (black)")
    success &= run_command(['poetry', 'run', 'isort', '--check-only', 'src', 'tests'], "Checking import order (isort)")
    success &= run_command(['poetry', 'run', 'flake8', 'src', 'tests'], "Running flake8 linting")
    return success


def format_code():
    """Format code using black and isort."""
    success = True
    success &= run_command(['poetry', 'run', 'black', 'src', 'tests'], "Formatting code with black")
    success &= run_command(['poetry', 'run', 'isort', 'src', 'tests'], "Sorting imports with isort")
    return success


def install():
    """Install dependencies."""
    success = True
    success &= run_command(['poetry', 'install'], "Installing dependencies")
    return success


def build():
    """Build the project."""
    return run_command(['poetry', 'build'], "Building project")


def clean():
    """Clean build artifacts and caches."""
    import shutil
    
    paths_to_clean = [
        '.pytest_cache',
        'htmlcov',
        'dist',
        'build',
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.pyd',
        '.coverage'
    ]
    
    for path_pattern in paths_to_clean:
        for path in Path('.').glob(path_pattern):
            if path.is_dir():
                print(f"Removing directory: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"Removing file: {path}")
                path.unlink()
    
    print("✅ Cleanup completed!")
    return True


def all_checks():
    """Run all checks (format, lint, test)."""
    success = True
    success &= format_code()
    success &= lint()
    success &= test_coverage()
    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Development task runner for sigrok-dev")
    parser.add_argument('task', choices=[
        'test', 'test-cov', 'lint', 'format', 'install', 'build', 'clean', 'all'
    ], help='Task to run')
    
    args = parser.parse_args()
    
    task_map = {
        'test': test,
        'test-cov': test_coverage,
        'lint': lint,
        'format': format_code,
        'install': install,
        'build': build,
        'clean': clean,
        'all': all_checks
    }
    
    success = task_map[args.task]()
    
    if not success:
        print(f"\n❌ Task '{args.task}' failed!")
        sys.exit(1)
    else:
        print(f"\n✅ Task '{args.task}' completed successfully!")


if __name__ == "__main__":
    main()
