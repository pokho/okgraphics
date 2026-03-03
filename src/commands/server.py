"""Server command schemas."""

from src.cli.types import CommandSchema, CommandOption, CommandExample

server_start_command = CommandSchema(
    name="server:start",
    aliases=["serve", "api"],
    category="Server",
    description="Start the API server",
    long_description="""
Start the FastAPI server for OK Print Designs.

The server provides REST endpoints for:
  - POST /generate/vector  - Generate vector graphics
  - POST /generate/anime   - Convert to anime style
  - GET  /loras/list       - List available LoRAs
  - GET  /health           - Health check

Models load on first request to minimize startup time.
""",
    handler="src.handlers.server:handle_start",
    options=[
        CommandOption(
            name="host",
            description="Host to bind",
            type="string",
            default="0.0.0.0",
        ),
        CommandOption(
            name="port",
            description="Port to bind",
            type="number",
            default=8000,
            aliases=["p"],
        ),
        CommandOption(
            name="reload",
            description="Enable auto-reload for development",
            type="boolean",
            default=False,
        ),
    ],
    examples=[
        CommandExample(
            command="server:start",
            description="Start server on default port 8000",
        ),
        CommandExample(
            command="serve --port 3000 --reload",
            description="Start on port 3000 with auto-reload",
        ),
    ],
    see_also=["model:list"],
)
