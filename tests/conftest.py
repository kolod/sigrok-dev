#!/usr/bin/env python3

"""
Configuration file for pytest.

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

import pytest

# Add src directory to Python path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_sigrok_cli_path(tmp_path):
    """Create a temporary sigrok-cli executable for testing."""
    sigrok_cli_path = tmp_path / "sigrok-cli"
    sigrok_cli_path.write_text("#!/bin/bash\necho 'sigrok-cli version test'")
    sigrok_cli_path.chmod(0o755)
    return str(sigrok_cli_path)


@pytest.fixture
def sample_vcd_file(tmp_path):
    """Create a sample VCD file for testing."""
    vcd_content = """$date
    Mon Jan 01 00:00:00 2024
$end
$version
    Test VCD file
$end
$timescale 1ns $end
$scope module testbench $end
$var wire 1 ! clk $end
$var wire 1 " data $end
$upscope $end
$enddefinitions $end
#0
0!
0"
#10
1!
#20
0!
1"
#30
1!
"""
    vcd_file = tmp_path / "test.vcd"
    vcd_file.write_text(vcd_content)
    return vcd_file


@pytest.fixture
def sample_output_file(tmp_path):
    """Create a sample output file path for testing."""
    return tmp_path / "output.sr"
