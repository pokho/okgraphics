"""CLI runtime - help generation and command execution."""

import argparse
import importlib
import logging
import sys
from collections import defaultdict
from typing import Any, Callable

from src.cli.types import CommandSchema

logger = logging.getLogger("okgraphics.cli")


def generate_help(commands: list[CommandSchema], prog: str = "okgraphics") -> str:
    """Generate main help text from command schemas."""
    # Group by category
    by_category: dict[str, list[CommandSchema]] = defaultdict(list)
    for cmd in commands:
        by_category[cmd.category].append(cmd)

    output = f"Usage: {prog} <command> [options]\n\n"
    output += "Local AI-powered print design system.\n\n"

    for category, cmds in sorted(by_category.items()):
        output += f"{category}:\n"
        for cmd in cmds:
            deprecated = " (deprecated)" if cmd.deprecated else ""
            output += f"  {cmd.name.ljust(28)} {cmd.description}{deprecated}\n"
        output += "\n"

    output += "Options:\n"
    output += "  -h, --help            Show this help\n"
    output += "  -v, --version         Show version\n"
    output += f"\nRun '{prog} <command> --help' for command details.\n"

    return output


def generate_command_help(schema: CommandSchema, prog: str = "okgraphics") -> str:
    """Generate detailed help for a single command."""
    output = ""

    output += f"Command: {schema.name}\n"
    if schema.aliases:
        output += f"Aliases: {', '.join(schema.aliases)}\n"

    output += f"\n{schema.description}\n"

    if schema.long_description:
        output += f"\n{schema.long_description.strip()}\n"

    if schema.positional:
        output += "\nArguments:\n"
        for pos in schema.positional:
            required = " (required)" if pos.required else ""
            default = f" [default: {pos.default}]" if pos.default is not None else ""
            output += f"  {pos.name.ljust(20)} {pos.description}{required}{default}\n"

    if schema.options:
        output += "\nOptions:\n"
        for opt in schema.options:
            flags = [f"--{opt.name}"]
            flags.extend(f"-{a}" for a in opt.aliases)
            flag_str = ", ".join(flags)
            required = " (required)" if opt.required else ""
            default = f" [default: {opt.default}]" if opt.default is not None and not opt.required else ""
            output += f"  {flag_str.ljust(24)} {opt.description}{required}{default}\n"

    if schema.examples:
        output += "\nExamples:\n"
        for ex in schema.examples:
            output += f"  {prog} {ex.command}\n"
            output += f"    {ex.description}\n"

    if schema.see_also:
        output += f"\nSee also: {', '.join(schema.see_also)}\n"

    return output


def _build_parser(schema: CommandSchema, prog: str) -> argparse.ArgumentParser:
    """Build an argparse parser from a command schema."""
    parser = argparse.ArgumentParser(
        prog=f"{prog} {schema.name}",
        description=schema.description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    # Add positional arguments
    for pos in schema.positional:
        parser.add_argument(
            pos.name,
            type=str if pos.type == "string" else int if pos.type == "number" else str,
            help=pos.description,
        )

    # Add options
    for opt in schema.options:
        flags = [f"--{opt.name}"]
        flags.extend(f"-{a}" for a in opt.aliases)

        kwargs: dict[str, Any] = {
            "help": opt.description,
        }

        if opt.type == "boolean":
            kwargs["action"] = "store_true"
            if opt.default:
                kwargs["default"] = True
        elif opt.type == "array":
            kwargs["nargs"] = "+"
        elif opt.type == "number":
            kwargs["type"] = float if "." in str(opt.default or 0) else int
        else:
            kwargs["type"] = str

        if opt.default is not None and opt.type != "boolean":
            kwargs["default"] = opt.default

        if opt.required and opt.type != "boolean":
            kwargs["required"] = True

        parser.add_argument(*flags, **kwargs)

    # Add help flag
    parser.add_argument("-h", "--help", action="store_true", help="Show this help")

    return parser


def _load_handler(handler_ref: str) -> Callable[..., Any]:
    """Load a handler function from a string reference.

    Args:
        handler_ref: Handler reference in format "module:function"
                     e.g., "src.handlers.generate:handle_vector"

    Returns:
        The handler function
    """
    module_path, func_name = handler_ref.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def execute_command(
    schema: CommandSchema,
    args: list[str],
    prog: str = "okgraphics",
) -> Any:
    """Parse args and execute a command handler."""
    # Check for help flag first (before argparse checks required args)
    if "-h" in args or "--help" in args:
        print(generate_command_help(schema, prog))
        return None

    # Check deprecation
    if schema.deprecated:
        replacement = f" Use '{schema.deprecated_by}' instead." if schema.deprecated_by else ""
        logger.warning(f"Deprecated command '{schema.name}' used.{replacement}")
        print(f"Warning: '{schema.name}' is deprecated.{replacement}", file=sys.stderr)

    # Build parser and parse
    parser = _build_parser(schema, prog)
    parsed = parser.parse_args(args)

    # Convert to dict and validate
    options = vars(parsed)

    # Remove help flag
    options.pop("help", None)

    # Validate options
    for opt in schema.options:
        if opt.required and options.get(opt.name) is None:
            raise ValueError(f"Missing required option: --{opt.name}")

        if opt.validate and options.get(opt.name) is not None:
            result = opt.validate(options[opt.name])
            if result is not True:
                raise ValueError(result or f"Invalid value for --{opt.name}")

    # Load and execute handler (lazy import)
    handler = _load_handler(schema.handler)
    return handler(**options)


def run_cli(
    commands: list[CommandSchema],
    prog: str = "okgraphics",
    version: str = "0.1.0",
) -> int:
    """Main CLI entry point."""
    # Build command lookup (including aliases)
    command_map: dict[str, CommandSchema] = {}
    for cmd in commands:
        command_map[cmd.name] = cmd
        for alias in cmd.aliases:
            command_map[alias] = cmd

    # Parse initial args
    if len(sys.argv) < 2:
        print(generate_help(commands, prog))
        return 0

    cmd_name = sys.argv[1]

    # Handle built-ins
    if cmd_name in ["-h", "--help"]:
        print(generate_help(commands, prog))
        return 0

    if cmd_name in ["-v", "--version"]:
        print(f"{prog} {version}")
        return 0

    # Find command
    schema = command_map.get(cmd_name)
    if not schema:
        logger.warning(f"Unknown command attempted: {cmd_name}")
        print(f"Unknown command: {cmd_name}", file=sys.stderr)
        print(f"Run '{prog} --help' for available commands.", file=sys.stderr)
        return 1

    logger.info(f"Running command: {cmd_name} {' '.join(sys.argv[2:])}".strip())

    # Execute
    try:
        result = execute_command(schema, sys.argv[2:], prog)
        logger.info(f"Command '{cmd_name}' completed successfully")
        return 0 if result is None else 0
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        logger.info("Cancelled by user")
        print("\nCancelled.", file=sys.stderr)
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
