"""Handlers for generation commands."""

from pathlib import Path

from src.models.loaders import ModelLoader
from src.pipelines.vector import VectorPipeline, AnimePipeline
from src.logging_config import get_logger

logger = get_logger("generate")

# Shared model loader (lazy loaded)
_loader: ModelLoader | None = None


def _get_loader() -> ModelLoader:
    """Get or create the shared model loader."""
    global _loader
    if _loader is None:
        _loader = ModelLoader("configs/config.yaml")
    return _loader


def handle_vector(
    prompt: str,
    lora: str = "vector_flat",
    width: int = 2400,
    height: int = 3200,
    steps: int = 30,
    guidance: float = 7.5,
    seed: int | None = None,
    output: str | None = None,
    no_save: bool = False,
) -> None:
    """Generate a vector-style graphic."""
    loader = _get_loader()
    pipeline = VectorPipeline(loader)

    logger.info(f"Generating vector: prompt='{prompt[:50]}...' lora={lora} size={width}x{height}")
    print(f"Generating: {prompt}")
    print(f"Size: {width}x{height}")
    print(f"LoRA: {lora}")
    print(f"Steps: {steps}, Guidance: {guidance}")

    if seed is not None:
        print(f"Seed: {seed}")

    image = pipeline.generate(
        prompt=prompt,
        lora=lora,
        width=width,
        height=height,
        steps=steps,
        guidance=guidance,
        seed=seed,
        save_output=not no_save,
    )

    if output:
        image.save(output)
        logger.info(f"Saved to: {output}")
        print(f"Saved to: {output}")

    logger.info("Vector generation complete")
    print("Done!")


def handle_anime(
    input: str,
    style: str = "anime_watercolor",
    strength: float = 0.70,
    steps: int = 35,
    guidance: float = 7.5,
    prompt: str | None = None,
    seed: int | None = None,
    output: str | None = None,
    no_save: bool = False,
) -> None:
    """Convert a photo to hand-drawn anime style."""
    loader = _get_loader()
    pipeline = AnimePipeline(loader)

    input_path = Path(input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input}")
        raise ValueError(f"Input file not found: {input}")

    logger.info(f"Converting to anime: input={input} style={style} strength={strength}")
    print(f"Converting: {input}")
    print(f"Style: {style}")
    print(f"Strength: {strength}")
    print(f"Steps: {steps}")

    if prompt:
        print(f"Prompt: {prompt}")
    if seed is not None:
        print(f"Seed: {seed}")

    image = pipeline.convert(
        input_image=str(input_path),
        style=style,
        strength=strength,
        steps=steps,
        guidance=guidance,
        custom_prompt=prompt,
        seed=seed,
        save_output=not no_save,
    )

    if output:
        image.save(output)
        logger.info(f"Saved to: {output}")
        print(f"Saved to: {output}")

    logger.info("Anime conversion complete")
    print("Done!")
