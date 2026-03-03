"""Model management command schemas."""

from src.cli.types import CommandSchema, CommandOption, CommandExample

model_list_command = CommandSchema(
    name="model:list",
    aliases=["models", "loras"],
    category="Model",
    description="List available LoRA adapters",
    long_description="""
List all available LoRA style adapters with their trigger words and
descriptions. Use the LoRA ID with generate:vector or generate:ghibli
to apply a specific style.
""",
    handler="src.handlers.model:handle_list",
    options=[],
    examples=[
        CommandExample(
            command="model:list",
            description="Show all available LoRA adapters",
        ),
    ],
    see_also=["generate:vector", "generate:ghibli"],
)
