"""Command schemas for OK Print Designs."""

from src.cli.types import CommandSchema, CommandOption, CommandExample

# --- Vector Generation ---

vector_command = CommandSchema(
    name="generate:vector",
    aliases=["vector", "gen:vector"],
    category="Generation",
    description="Generate vector-style graphic for print",
    long_description="""
Generate print-ready vector-style graphics using SDXL + LoRA adapters.

Outputs are saved to outputs/vector/ with 300 DPI metadata for professional
printing. Supports multiple LoRA styles for different aesthetics.

Default size (2400x3200) produces an 8x10.67" print at 300 DPI.
""",
    handler="src.handlers.generate:handle_vector",
    positional=[
        CommandOption(
            name="prompt",
            description="Text description of the image to generate",
            type="string",
            required=True,
        ),
    ],
    options=[
        CommandOption(
            name="lora",
            description="LoRA style adapter (vector_flat, vector_illustration)",
            type="string",
            default="vector_flat",
            aliases=["l"],
        ),
        CommandOption(
            name="width",
            description="Image width in pixels",
            type="number",
            default=2400,
            aliases=["W"],
        ),
        CommandOption(
            name="height",
            description="Image height in pixels",
            type="number",
            default=3200,
            aliases=["H"],
        ),
        CommandOption(
            name="steps",
            description="Inference steps (higher = more detail, slower)",
            type="number",
            default=30,
            aliases=["s"],
        ),
        CommandOption(
            name="guidance",
            description="Guidance scale for prompt adherence",
            type="number",
            default=7.5,
            aliases=["g"],
        ),
        CommandOption(
            name="seed",
            description="Random seed for reproducibility",
            type="number",
            default=None,
        ),
        CommandOption(
            name="output",
            description="Output file path (default: auto-generated)",
            type="string",
            default=None,
            aliases=["o"],
        ),
        CommandOption(
            name="no-save",
            description="Don't save to outputs directory",
            type="boolean",
            default=False,
        ),
    ],
    examples=[
        CommandExample(
            command='generate:vector "mountain landscape at sunset"',
            description="Generate a mountain landscape (default settings)",
        ),
        CommandExample(
            command='generate:vector "cute cat" --lora vector_illustration --width 1024 --height 1024',
            description="Generate sticker-style graphic for web",
        ),
        CommandExample(
            command='vector "abstract pattern" --steps 40 --seed 42 --output pattern.png',
            description="Generate with custom settings and seed",
        ),
    ],
    see_also=["generate:ghibli", "model:list"],
)

# --- Ghibli Style Transfer ---

ghibli_command = CommandSchema(
    name="generate:ghibli",
    aliases=["ghibli", "gen:ghibli", "style:ghibli"],
    category="Generation",
    description="Convert photo to Ghibli/anime style",
    long_description="""
Convert photos to anime/Ghibli style using SDXL img2img + LoRA adapters.

Uses image-to-image transformation to preserve composition while applying
the anime style. Strength controls how much the image is transformed
(0.5 = subtle, 0.9 = dramatic).

Images larger than 1536px are automatically resized for optimal quality.
""",
    handler="src.handlers.generate:handle_ghibli",
    positional=[
        CommandOption(
            name="input",
            description="Path to input image file",
            type="string",
            required=True,
        ),
    ],
    options=[
        CommandOption(
            name="style",
            description="LoRA style (ghibli_style, anime_general, vector_flat)",
            type="string",
            default="ghibli_style",
            aliases=["s"],
        ),
        CommandOption(
            name="strength",
            description="Transformation strength (0.0-1.0)",
            type="number",
            default=0.70,
        ),
        CommandOption(
            name="steps",
            description="Inference steps (higher = more detail, slower)",
            type="number",
            default=35,
        ),
        CommandOption(
            name="guidance",
            description="Guidance scale for prompt adherence",
            type="number",
            default=7.5,
            aliases=["g"],
        ),
        CommandOption(
            name="prompt",
            description="Additional style hints",
            type="string",
            default=None,
            aliases=["p"],
        ),
        CommandOption(
            name="seed",
            description="Random seed for reproducibility",
            type="number",
            default=None,
        ),
        CommandOption(
            name="output",
            description="Output file path (default: auto-generated)",
            type="string",
            default=None,
            aliases=["o"],
        ),
        CommandOption(
            name="no-save",
            description="Don't save to outputs directory",
            type="boolean",
            default=False,
        ),
    ],
    examples=[
        CommandExample(
            command='generate:ghibli photo.jpg',
            description="Convert photo to Ghibli style (default settings)",
        ),
        CommandExample(
            command='ghibli portrait.png --style anime_general --strength 0.55',
            description="Lighter anime conversion",
        ),
        CommandExample(
            command='style:ghibli landscape.jpg --strength 0.85 --prompt "sunset lighting"',
            description="Strong conversion with custom prompt",
        ),
    ],
    see_also=["generate:vector", "model:list"],
)
