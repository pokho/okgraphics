"""Handlers for model management commands."""

from src.models.loaders import ModelLoader


def handle_list() -> None:
    """List available LoRA adapters."""
    loader = ModelLoader("configs/config.yaml")
    loras = loader.list_loras()

    print("Available LoRA Adapters:\n")
    print(f"{'ID':<20} {'Trigger Word':<30} Description")
    print("-" * 80)

    for lora in loras:
        trigger = lora.get("trigger_word", "")
        desc = lora.get("description", "")
        print(f"{lora['id']:<20} {trigger:<30} {desc}")

    print()
    print("Usage: okgraphics generate:vector --lora <id>")
    print("       okgraphics generate:ghibli --style <id>")
