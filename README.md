# Sigrok Development Tools

Development tools for the sigrok signal analysis software suite.

## Description

This package provides Python tools for working with sigrok-cli, including utilities for:
- Finding and executing sigrok-cli installations
- Converting between different signal file formats (VCD, sigrok, etc.)
- Automating signal analysis workflows

## Installation

### Prerequisites

- Python 3.13 or higher
- Poetry (for development)
- Git (for cloning submodules)

 ### Git submodules

 This repository uses Git submodules. After cloning (or when pulling updates), initialize and update them:

 ```bash
 # If you already cloned the repo
 git submodule update --init --recursive

 # Recommended when cloning for the first time (does init+update in one step)
 git clone --recurse-submodules https://github.com/kolod/sigrok-dev.git
 cd sigrok-dev

 # When pulling new changes later
 git pull
 git submodule update --init --recursive

 # Optional: update submodules to the latest upstream commits (not just pinned revisions)
 git submodule update --init --recursive --remote
 ```

### Working with Sigrok Submodule Forks

This repository contains 3 Git submodules that are forks of the original sigrok repositories. To make synchronized changes across all submodules and create PRs to the upstream repositories:

#### Prerequisites
- GitHub CLI installed and authenticated: `gh auth login`
- Your fork repositories should have upstream remotes configured

#### Making Changes Across All Submodules

```powershell
# Define your branch name for consistent naming across all repos
$branchName = "feature/my-changes"  # Replace with your actual branch name

# Step 1: Create the same branch in all submodules
git submodule foreach "git checkout -b $branchName"

# Step 2: Make your changes in each submodule
# (Edit files in libsigrokdecode/, sigrok-dumps/, sigrok-test/ as needed)

# Step 3: Commit changes in each submodule
git submodule foreach "git add -A && git commit -m 'Your commit message here'"

# Step 4: Push branches to your fork repositories
git submodule foreach "git push -u origin $branchName"

# Step 5: Create PRs to upstream repositories
git submodule foreach "gh pr create --title 'Your PR Title' --body 'Your PR description' --base main"
```

#### Alternative: Work in each submodule individually

```powershell
$branchName = "feature/my-changes"

# Work on libsigrokdecode
cd libsigrokdecode
git checkout -b $branchName
# Make your changes...
git add -A
git commit -m "libsigrokdecode: your changes"
git push -u origin $branchName
gh pr create --title "libsigrokdecode: Your PR Title" --body "Description" --base main
cd ..

# Work on sigrok-dumps  
cd sigrok-dumps
git checkout -b $branchName
# Make your changes...
git add -A
git commit -m "sigrok-dumps: your changes"
git push -u origin $branchName  
gh pr create --title "sigrok-dumps: Your PR Title" --body "Description" --base main
cd ..

# Work on sigrok-test
cd sigrok-test
git checkout -b $branchName
# Make your changes...
git add -A
git commit -m "sigrok-test: your changes"
git push -u origin $branchName
gh pr create --title "sigrok-test: Your PR Title" --body "Description" --base main
cd ..
```

#### Update Superproject with New Submodule Commits

After your PRs are merged (or if you want to update the main repository to point to your new commits):

```powershell
# Update submodule pointers in the main repository
git add libsigrokdecode sigrok-dumps sigrok-test
git commit -m "Update submodules to latest commits"
git push

# Or create a PR for the superproject changes
$superBranch = "chore/update-submodules-$(Get-Date -Format yyyyMMdd-HHmmss)"
git checkout -b $superBranch  
git add libsigrokdecode sigrok-dumps sigrok-test
git commit -m "chore: update submodules to include latest changes"
git push -u origin $superBranch
gh pr create --fill
```

#### Useful Tips

- Check submodule status: `git submodule status`
- See which submodules have uncommitted changes: `git submodule foreach "git status --porcelain"`
- Reset all submodules to match superproject: `git submodule foreach "git reset --hard"`
- Ensure upstream remotes are configured in each submodule:
  ```powershell
  git submodule foreach "git remote add upstream <original-sigrok-repo-url> || true"
  git submodule foreach "git fetch upstream"
  ```
### Using Poetry

```bash
# Clone the repository
git clone https://github.com/kolod/sigrok-dev.git
cd sigrok-dev

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
pip install sigrok-dev
```

## Usage

```python
from sigrok_dev.sigrok_cli import SigrokCli

# Initialize sigrok-cli wrapper
cli = SigrokCli()

# Run sigrok-cli commands
result = cli.run_sigrok_cli(['--list-devices'])

# Import VCD file to sigrok format
cli.import_file(
    output_file=Path('output.sr'),
    input_file=Path('input.vcd'),
    input_format='vcd'
)
```

## Development

### Setup

```bash
# Install development dependencies
poetry install

# Install pre-commit hooks (optional)
poetry run pre-commit install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src/sigrok_dev --cov-report=html

# Run basic tests without pytest
poetry run python tests/run_basic_tests.py

# Using the development script
poetry run python dev.py test
poetry run python dev.py test-cov
```

### Code Quality

```bash
# Format code
poetry run python dev.py format

# Run linting
poetry run python dev.py lint

# Run all checks
poetry run python dev.py all
```

### Available Development Tasks

Using the `dev.py` script:

- `test` - Run all tests
- `test-cov` - Run tests with coverage report
- `lint` - Run linting checks (black, isort, flake8)
- `format` - Format code (black, isort)
- `install` - Install dependencies
- `build` - Build the project
- `clean` - Clean build artifacts and caches
- `all` - Run all checks (format, lint, test)

Example:
```bash
poetry run python dev.py format
poetry run python dev.py test
poetry run python dev.py all
```

### Project Structure

```
sigrok-dev/
├── src/
│   └── sigrok_dev/
│       ├── __init__.py
│       └── sigrok_cli.py          # Main sigrok-cli wrapper
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # pytest configuration
│   ├── test_sigrok_cli.py         # Tests for sigrok_cli module
│   └── run_basic_tests.py         # Basic test runner
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD
├── dev.py                         # Development task runner
├── pyproject.toml                 # Poetry configuration
├── poetry.lock                    # Lock file
└── README.md                      # This file
```

## Testing

The project includes comprehensive tests with:

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test interaction with real sigrok-cli (if available)
- **Mocking**: Mock external dependencies for reliable testing
- **Coverage**: 98% code coverage achieved

### Test Categories

1. **Initialization Tests**: Test sigrok-cli discovery and path resolution
2. **Execution Tests**: Test command execution, error handling, and timeouts
3. **File Import Tests**: Test VCD and other format imports
4. **Error Handling Tests**: Test various failure scenarios

### Running Specific Tests

```bash
# Run specific test class
poetry run pytest tests/test_sigrok_cli.py::TestSigrokCli -v

# Run specific test method
poetry run pytest tests/test_sigrok_cli.py::TestSigrokCli::test_init_with_sigrok_cli_in_path -v

# Run integration tests only
poetry run pytest tests/test_sigrok_cli.py::TestSigrokCliIntegration -v
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `poetry run python dev.py all`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## Requirements

### Runtime Dependencies

- `rich` (>=14.1.0) - Rich text and beautiful formatting

### Development Dependencies

- `pytest` (>=8.0.0) - Testing framework
- `pytest-cov` (>=5.0.0) - Coverage reporting
- `pytest-mock` (>=3.0.0) - Mocking utilities
- `black` (>=24.0.0) - Code formatting
- `isort` (>=5.0.0) - Import sorting
- `flake8` (>=7.0.0) - Code linting

## License

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

## Author

- **Oleksandr Kolodkin** - *oleksandr.kolodkin@ukr.net*

## Changelog

### Version 0.1.0

- Initial release
- SigrokCli class for sigrok-cli wrapper functionality
- VCD file import capabilities
- Comprehensive test suite with 98% coverage
- Development tools and CI/CD setup
