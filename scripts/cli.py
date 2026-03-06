#!/usr/bin/env python3
"""OK Print Designs CLI - Schema-based command interface.

Usage:
    okgraphics <command> [options]

Commands:
    generate:vector    Generate vector-style graphic for print
    generate:ghibli    Convert photo to Ghibli/anime style
    server:start       Start the API server
    model:list         List available LoRA adapters

Run 'okgraphics --help' for full command list.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.runtime import run_cli
from src.commands import ALL_COMMANDS
from src.logging_config import setup_logging


def main() -> int:
    """Main CLI entry point."""
    setup_logging()
    return run_cli(
        commands=ALL_COMMANDS,
        prog="okgraphics",
        version="0.1.0",
    )


if __name__ == "__main__":
    sys.exit(main())
