"""Command registry - all available CLI commands."""

from src.commands.generate import vector_command, ghibli_command
from src.commands.server import server_start_command
from src.commands.model import model_list_command

# All commands registered here
ALL_COMMANDS = [
    vector_command,
    ghibli_command,
    server_start_command,
    model_list_command,
]

# Categories for help organization
CATEGORIES = {
    "Generation": ["generate:vector", "generate:ghibli"],
    "Server": ["server:start"],
    "Model": ["model:list"],
}
