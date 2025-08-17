#!/usr/bin/env python3

"""
Simple test runner script that can run basic tests without pytest.

This file is part of sigrok-dev-tools.
Copyright (C) 2025 Oleksandr Kolodkin <oleksandr.kolodkin@ukr.net>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

import sys
from pathlib import Path
from subprocess import CompletedProcess  # noqa: E402
from unittest.mock import Mock, patch

# Add src to the path to import our module
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from sigrok_dev.sigrok_cli import SigrokCli  # noqa: E402


def test_sigrok_cli_basic():
    """Basic test for SigrokCli initialization."""
    print("Testing SigrokCli basic functionality...")

    with (
        patch("sigrok_dev.sigrok_cli.which") as mock_which,
        patch("sigrok_dev.sigrok_cli.print"),
    ):

        mock_which.return_value = "/usr/bin/sigrok-cli"

        sigrok_cli = SigrokCli()

        assert sigrok_cli.sigrok_cli_path == "/usr/bin/sigrok-cli"
        print("✓ SigrokCli initialization test passed")


def test_sigrok_cli_not_found():
    """Test when sigrok-cli is not found."""
    print("Testing SigrokCli when not found...")

    with (
        patch("sigrok_dev.sigrok_cli.which") as mock_which,
        patch("sigrok_dev.sigrok_cli.Path") as mock_path_class,
    ):

        mock_which.return_value = None

        # Mock Path to return False for all locations
        mock_path = Mock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        sigrok_cli = SigrokCli()

        assert sigrok_cli.sigrok_cli_path is None
        print("✓ SigrokCli not found test passed")


def test_run_sigrok_cli():
    """Test running sigrok-cli."""
    print("Testing run_sigrok_cli...")

    with (
        patch("sigrok_dev.sigrok_cli.which") as mock_which,
        patch("sigrok_dev.sigrok_cli.run") as mock_run,
        patch("sigrok_dev.sigrok_cli.print"),
    ):

        mock_which.return_value = "/usr/bin/sigrok-cli"
        expected_result = CompletedProcess(
            args=["sigrok-cli", "--version"],
            returncode=0,
            stdout="version info",
            stderr="",
        )
        mock_run.return_value = expected_result

        sigrok_cli = SigrokCli()
        result = sigrok_cli.run_sigrok_cli(["--version"])

        assert result == expected_result
        print("✓ run_sigrok_cli test passed")
        print("✓ run_sigrok_cli test passed")


if __name__ == "__main__":
    print("Running basic tests for sigrok_dev.sigrok_cli module...\n")

    try:
        test_sigrok_cli_basic()
        test_sigrok_cli_not_found()
        test_run_sigrok_cli()

        print("\n✓ All basic tests passed!")
        print("Install pytest to run the full test suite: poetry install")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
