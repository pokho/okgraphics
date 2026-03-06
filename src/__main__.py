"""CLI entry point for okgraphics."""

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
    import sys
    sys.exit(main())
