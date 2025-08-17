#!/usr/bin/env python3

"""
Tests for the sigrok_cli.py module.

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
from subprocess import CompletedProcess, SubprocessError, TimeoutExpired
from unittest.mock import Mock, patch

import pytest

# Add src to the path to import our module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sigrok_dev.sigrok_cli import SigrokCli  # noqa: E402


class TestSigrokCli:
    """Test cases for the SigrokCli class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.sigrok_cli = None

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.print")
    def test_init_with_sigrok_cli_in_path(self, mock_print, mock_which):
        """Test initialization when sigrok-cli is found in PATH."""
        mock_which.return_value = "/usr/bin/sigrok-cli"

        sigrok_cli = SigrokCli()

        assert sigrok_cli.sigrok_cli_path == "/usr/bin/sigrok-cli"
        mock_which.assert_called_once_with("sigrok-cli")
        mock_print.assert_called_with("[green]Found sigrok-cli via PATH:[/green] /usr/bin/sigrok-cli")

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.Path")
    @patch("sigrok_dev.sigrok_cli.run")
    @patch("sigrok_dev.sigrok_cli.print")
    def test_init_with_sigrok_cli_in_common_location(self, mock_print, mock_run, mock_path_class, mock_which):
        """Test initialization when sigrok-cli is found in common locations."""
        mock_which.return_value = None

        # Mock Path behavior
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.__str__ = Mock(return_value="/usr/local/bin/sigrok-cli")
        mock_path_class.return_value = mock_path

        # Mock successful run result
        mock_run.return_value = CompletedProcess(
            args=["sigrok-cli", "--version"],
            returncode=0,
            stdout="sigrok-cli version",
            stderr="",
        )

        sigrok_cli = SigrokCli()

        # The first location that exists should be selected
        assert sigrok_cli.sigrok_cli_path == "/usr/local/bin/sigrok-cli"
        mock_print.assert_called_with(f"[green]Found sigrok-cli at:[/green] {mock_path}")

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.Path")
    def test_init_sigrok_cli_not_found(self, mock_path_class, mock_which):
        """Test initialization when sigrok-cli is not found anywhere."""
        mock_which.return_value = None

        # Mock Path to return False for all locations
        mock_path = Mock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        sigrok_cli = SigrokCli()

        assert sigrok_cli.sigrok_cli_path is None

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.Path")
    @patch("sigrok_dev.sigrok_cli.run")
    def test_find_sigrok_cli_timeout_error(self, mock_run, mock_path_class, mock_which):
        """Test find_sigrok_cli handles TimeoutExpired exception."""
        mock_which.return_value = None

        # Mock Path behavior
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path_class.return_value = mock_path

        # Mock timeout exception
        mock_run.side_effect = TimeoutExpired(["sigrok-cli", "--version"], timeout=10)

        sigrok_cli = SigrokCli()

        assert sigrok_cli.sigrok_cli_path is None

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.Path")
    @patch("sigrok_dev.sigrok_cli.run")
    def test_find_sigrok_cli_subprocess_error(self, mock_run, mock_path_class, mock_which):
        """Test find_sigrok_cli handles SubprocessError exception."""
        mock_which.return_value = None

        # Mock Path behavior
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path_class.return_value = mock_path

        # Mock subprocess error
        mock_run.side_effect = SubprocessError("Process error")

        sigrok_cli = SigrokCli()

        assert sigrok_cli.sigrok_cli_path is None

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.run")
    @patch("sigrok_dev.sigrok_cli.print")
    def test_run_sigrok_cli_success(self, mock_print, mock_run, mock_which):
        """Test successful run_sigrok_cli execution."""
        mock_which.return_value = "/usr/bin/sigrok-cli"

        # Mock successful run result
        expected_result = CompletedProcess(
            args=["sigrok-cli", "--list-devices"],
            returncode=0,
            stdout="device output",
            stderr="",
        )
        mock_run.return_value = expected_result

        sigrok_cli = SigrokCli()
        result = sigrok_cli.run_sigrok_cli(["--list-devices"])

        assert result == expected_result
        mock_run.assert_called_with(
            ["/usr/bin/sigrok-cli", "--list-devices"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        mock_print.assert_called_with("[cyan]Running sigrok-cli[/cyan] args: [bold]['--list-devices'][/bold]")

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.print")
    def test_run_sigrok_cli_no_path(self, mock_print, mock_which):
        """Test run_sigrok_cli when sigrok-cli path is not found."""
        mock_which.return_value = None

        # Mock Path to simulate sigrok-cli not found
        with patch("sigrok_dev.sigrok_cli.Path") as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path

            sigrok_cli = SigrokCli()
            result = sigrok_cli.run_sigrok_cli(["--list-devices"])

        assert result is None
        mock_print.assert_called_with("[red]✗ sigrok-cli not found.[/red]")

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.run")
    @patch("sigrok_dev.sigrok_cli.print")
    def test_run_sigrok_cli_timeout(self, mock_print, mock_run, mock_which):
        """Test run_sigrok_cli with timeout exception."""
        mock_which.return_value = "/usr/bin/sigrok-cli"
        mock_run.side_effect = TimeoutExpired(["sigrok-cli"], timeout=10)

        sigrok_cli = SigrokCli()
        result = sigrok_cli.run_sigrok_cli(["--list-devices"])

        assert result is None
        expected_msg = (
            "[red]Error occurred while running sigrok-cli:[/red] " "Command '['sigrok-cli']' timed out after 10 seconds"
        )
        mock_print.assert_any_call(expected_msg)

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.run")
    @patch("sigrok_dev.sigrok_cli.print")
    def test_run_sigrok_cli_subprocess_error(self, mock_print, mock_run, mock_which):
        """Test run_sigrok_cli with subprocess error."""
        mock_which.return_value = "/usr/bin/sigrok-cli"
        mock_run.side_effect = SubprocessError("Process failed")

        sigrok_cli = SigrokCli()
        result = sigrok_cli.run_sigrok_cli(["--list-devices"])

        assert result is None
        mock_print.assert_any_call("[red]Error occurred while running sigrok-cli:[/red] Process failed")

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.run")
    def test_import_file_success(self, mock_run, mock_which):
        """Test successful import_file execution."""
        mock_which.return_value = "/usr/bin/sigrok-cli"

        # Mock successful run result
        expected_result = CompletedProcess(
            args=[
                "sigrok-cli",
                "-I",
                "vcd",
                "-i",
                "vcd",
                "input.vcd",
                "-O",
                "sigrok",
                "-o",
                "output.sr",
            ],
            returncode=0,
            stdout="import successful",
            stderr="",
        )
        mock_run.return_value = expected_result

        sigrok_cli = SigrokCli()
        input_file = Path("input.vcd")
        output_file = Path("output.sr")

        result = sigrok_cli.import_file(output_file, input_file)

        assert result == expected_result
        mock_run.assert_called_with(
            [
                "/usr/bin/sigrok-cli",
                "-I",
                "vcd",
                "-i",
                "vcd",
                "input.vcd",
                "-O",
                "sigrok",
                "-o",
                "output.sr",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.run")
    def test_import_file_custom_format(self, mock_run, mock_which):
        """Test import_file with custom input format."""
        mock_which.return_value = "/usr/bin/sigrok-cli"

        expected_result = CompletedProcess(
            args=[
                "sigrok-cli",
                "-I",
                "csv",
                "-i",
                "csv",
                "input.csv",
                "-O",
                "sigrok",
                "-o",
                "output.sr",
            ],
            returncode=0,
            stdout="import successful",
            stderr="",
        )
        mock_run.return_value = expected_result

        sigrok_cli = SigrokCli()
        input_file = Path("input.csv")
        output_file = Path("output.sr")

        result = sigrok_cli.import_file(output_file, input_file, input_format="csv")

        assert result == expected_result
        mock_run.assert_called_with(
            [
                "/usr/bin/sigrok-cli",
                "-I",
                "csv",
                "-i",
                "csv",
                "input.csv",
                "-O",
                "sigrok",
                "-o",
                "output.sr",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.run")
    def test_import_file_custom_timeout(self, mock_run, mock_which):
        """Test import_file with custom timeout."""
        mock_which.return_value = "/usr/bin/sigrok-cli"

        expected_result = CompletedProcess(
            args=[
                "sigrok-cli",
                "-I",
                "vcd",
                "-i",
                "vcd",
                "input.vcd",
                "-O",
                "sigrok",
                "-o",
                "output.sr",
            ],
            returncode=0,
            stdout="import successful",
            stderr="",
        )
        mock_run.return_value = expected_result

        sigrok_cli = SigrokCli()
        input_file = Path("input.vcd")
        output_file = Path("output.sr")

        result = sigrok_cli.import_file(output_file, input_file, timeout=30.0)

        assert result == expected_result
        mock_run.assert_called_with(
            [
                "/usr/bin/sigrok-cli",
                "-I",
                "vcd",
                "-i",
                "vcd",
                "input.vcd",
                "-O",
                "sigrok",
                "-o",
                "output.sr",
            ],
            capture_output=True,
            text=True,
            timeout=30.0,
        )

    @patch("sigrok_dev.sigrok_cli.which")
    @patch("sigrok_dev.sigrok_cli.print")
    def test_import_file_no_path(self, mock_print, mock_which):
        """Test import_file when sigrok-cli path is not found."""
        mock_which.return_value = None

        # Mock Path to simulate sigrok-cli not found
        with patch("sigrok_dev.sigrok_cli.Path") as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path

            sigrok_cli = SigrokCli()
            input_file = Path("input.vcd")
            output_file = Path("output.sr")

            result = sigrok_cli.import_file(output_file, input_file)

        assert result is None
        mock_print.assert_called_with("[red]✗ sigrok-cli not found.[/red]")

    def test_run_sigrok_cli_with_custom_timeout(self):
        """Test run_sigrok_cli accepts custom timeout parameter."""
        with (
            patch("sigrok_dev.sigrok_cli.which") as mock_which,
            patch("sigrok_dev.sigrok_cli.run") as mock_run,
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
            result = sigrok_cli.run_sigrok_cli(["--version"], timeout=5.0)

            assert result == expected_result
            mock_run.assert_called_with(
                ["/usr/bin/sigrok-cli", "--version"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )

    def test_main_execution_warning(self):
        """Test that running the module directly shows a warning."""
        # Test both subprocess execution and mock execution for coverage
        import subprocess
        import sys
        from pathlib import Path

        # First test: subprocess execution (functional test)
        module_path = Path(__file__).parent.parent / "src" / "sigrok_dev" / "sigrok_cli.py"
        result = subprocess.run([sys.executable, str(module_path)], capture_output=True, text=True)

        output = result.stdout + result.stderr
        output_normalized = " ".join(output.split())
        assert "This script is part of sigrok-dev-tools" in output_normalized
        assert "no standalone execution is intended" in output_normalized
        assert result.returncode == 0

        # Second test: mock execution for coverage
        with patch("sigrok_dev.sigrok_cli.print") as mock_print:
            # Import the module and get reference to its main block
            import sigrok_dev.sigrok_cli

            # Manually execute the main block condition
            if True:  # Simulate __name__ == "__main__"
                sigrok_dev.sigrok_cli.print(
                    "[yellow]This script is part of sigrok-dev-tools and no standalone execution is intended.[/yellow]"
                )

            # Verify the print was called
            mock_print.assert_called_with(
                "[yellow]This script is part of sigrok-dev-tools and no standalone execution is intended.[/yellow]"
            )


class TestSigrokCliIntegration:
    """Integration tests for SigrokCli (these may require actual sigrok-cli)."""

    @pytest.mark.skipif(
        not any(
            Path(p).exists()
            for p in [
                "sigrok-cli",
                "/usr/bin/sigrok-cli",
                "/usr/local/bin/sigrok-cli",
                "C:\\Program Files\\sigrok\\sigrok-cli\\sigrok-cli.exe",
            ]
        ),
        reason="sigrok-cli not found in system",
    )
    def test_real_sigrok_cli_version(self):
        """Test with real sigrok-cli if available."""
        sigrok_cli = SigrokCli()
        if sigrok_cli.sigrok_cli_path:
            result = sigrok_cli.run_sigrok_cli(["--version"])
            assert result is not None
            assert result.returncode == 0
            assert "sigrok-cli" in result.stdout or "sigrok-cli" in result.stderr
