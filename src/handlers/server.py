"""Handlers for server commands."""

import uvicorn


def handle_start(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """Start the API server."""
    print(f"Starting OK Print Designs API on {host}:{port}")
    print("Models will load on first request.")
    print()
    print("Endpoints:")
    print("  POST /generate/vector  - Generate vector graphics")
    print("  POST /generate/ghibli  - Convert to anime style")
    print("  GET  /loras/list       - List available LoRAs")
    print("  GET  /health           - Health check")
    print()

    uvicorn.run(
        "src.api.server:app",
        host=host,
        port=port,
        reload=reload,
    )
