"""CLI type definitions for schema-based command system."""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class CommandOption:
    """Definition of a command option/flag."""

    name: str
    description: str
    type: str = "string"  # string, number, boolean, array
    required: bool = False
    default: Any = None
    aliases: list[str] = field(default_factory=list)
    validate: Callable[[Any], bool | str] | None = None


@dataclass
class CommandExample:
    """Usage example for a command."""

    command: str
    description: str


@dataclass
class CommandSchema:
    """Schema definition for a CLI command - single source of truth.

    Handler is stored as a string (module:function) and loaded lazily
    to avoid importing heavy dependencies at module load time.
    """

    # Identity (all required, no defaults)
    name: str
    category: str
    description: str
    handler: str  # Handler reference as "module:function" string

    # Optional fields with defaults
    aliases: list[str] = field(default_factory=list)
    long_description: str | None = None
    options: list[CommandOption] = field(default_factory=list)
    positional: list[CommandOption] = field(default_factory=list)
    examples: list[CommandExample] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    deprecated: bool = False
    deprecated_by: str | None = None
