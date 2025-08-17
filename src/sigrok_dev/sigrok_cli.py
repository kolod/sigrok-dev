#!/usr/bin/env python3

"""
A wrapper for locating and running the sigrok-cli tool.

This module provides the SigrokCli class, which helps find the sigrok-cli
executable on the system, run it with specified arguments, and import
signal files (e.g., VCD to sigrok format) using sigrok-cli.

Typical usage:
    cli = SigrokCli()
    result = cli.import_file(output_file=Path("out.sr"), input_file=Path("in.vcd"))

This file is part of sigrok-dev-tools.

Copyright (C) 2025-... Oleksandr Kolodkin <oleksandr.kolodkin@ukr.net>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, SubprocessError, TimeoutExpired, run
from typing import List, Optional

from rich import print


class SigrokCli(object):
    sigrok_cli_path: str | None = None

    def __init__(self):
        self.find_sigrok_cli()

    def find_sigrok_cli(self) -> None:
        """
        Find the full path to sigrok-cli executable.

        Returns:
            str: Path to sigrok-cli executable or None if not found
        """

        # Initialize
        self.sigrok_cli_path = None

        # First try using shutil.which (checks PATH)
        self.sigrok_cli_path = which("sigrok-cli")
        if self.sigrok_cli_path:
            print(f"[green]Found sigrok-cli via PATH:[/green] {self.sigrok_cli_path}")
            return self.sigrok_cli_path

        # Common sigrok-cli installation locations
        common_locations = [
            # Windows locations
            "C:\\Program Files\\sigrok\\sigrok-cli\\sigrok-cli.exe",
            "C:\\Program Files (x86)\\sigrok\\sigrok-cli\\sigrok-cli.exe",
            "C:\\sigrok\\sigrok-cli\\sigrok-cli.exe",
            # Linux/macOS locations
            "/usr/bin/sigrok-cli",
            "/usr/local/bin/sigrok-cli",
            "/opt/sigrok/bin/sigrok-cli",
            # Portable/development locations
            "./sigrok-cli",
            "../sigrok-cli/sigrok-cli",
        ]

        # Check common locations
        for location in common_locations:
            path = Path(location)
            if path.exists() and path.is_file():
                try:
                    # Test if the executable works
                    result = run(
                        [str(path), "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        print(f"[green]Found sigrok-cli at:[/green] {path}")
                        self.sigrok_cli_path = str(path)
                        return
                except (TimeoutExpired, SubprocessError):
                    continue

        return None

    def run_sigrok_cli(self, args: List[str], timeout: float = 10) -> Optional[CompletedProcess]:
        """
        Run the sigrok-cli with the given arguments.

        Args:
            args (list): List of arguments to pass to sigrok-cli.

        Returns:
            CompletedProcess: The result of the sigrok-cli execution.
        """
        if not self.sigrok_cli_path:
            print("[red]✗ sigrok-cli not found.[/red]")
            return None

        print(f"[cyan]Running sigrok-cli[/cyan] args: [bold]{args}[/bold]")

        try:
            result = run(
                [self.sigrok_cli_path] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result

        except (TimeoutExpired, SubprocessError) as e:
            print(f"[red]Error occurred while running sigrok-cli:[/red] {e}")
            return None

    def import_file(
        self,
        output_file: Path,
        input_file: Path,
        input_format: str = "vcd",
        timeout: float = 10,
    ) -> Optional[CompletedProcess]:
        """
        Import signals from a VCD file using sigrok-cli.

        Args:
            input_file (Path): Path to the input file.
            output_file (Path): Path to the output file.
            timeout (float): Timeout for the sigrok-cli command.

        Returns:
            Optional[CompletedProcess]: The result of the sigrok-cli execution.
        """
        if not self.sigrok_cli_path:
            print("[red]✗ sigrok-cli not found.[/red]")
            return None

        args = [
            "-I",
            input_format,
            "-i",
            input_format,
            str(input_file),
            "-O",
            "sigrok",
            "-o",
            str(output_file),
        ]
        return self.run_sigrok_cli(args, timeout=timeout)


if __name__ == "__main__":
    print("[yellow]This script is part of sigrok-dev-tools and no standalone execution is intended.[/yellow]")
