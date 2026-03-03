"""Handler module for OK Print Designs CLI.

Handlers are imported lazily by the CLI runtime to avoid
loading heavy dependencies (torch, diffusers) at module load time.
"""

# Handlers are loaded via src.cli.runtime._load_handler()
# using string references like "src.handlers.generate:handle_vector"
