"""Simplified pipelines - SDXL only with LoRA adapters."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
from PIL import Image

from src.models.loaders import ModelLoader

logger = logging.getLogger(__name__)


class VectorPipeline:
    """
    Generate vector-style graphics using SDXL + LoRA.

    Use cases:
    - Print graphics at 300 DPI
    - Clean line art
    - Flat illustrations
    """

    def __init__(self, loader: ModelLoader):
        self.loader = loader
        self.config = loader.config
        self.output_dir = Path(self.config.get("output", {}).get("base_dir", "outputs"))

    def _get_output_path(self, prompt: str, subdir: str = "vector") -> Path:
        """Generate output file path."""
        out_dir = self.output_dir / self.config.get("output", {}).get("subdirs", {}).get(subdir, subdir)
        out_dir.mkdir(parents=True, exist_ok=True)

        naming = self.config.get("output", {}).get("naming", {})
        parts = []

        if naming.get("include_timestamp", True):
            parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))

        if naming.get("include_prompt", True):
            max_len = naming.get("max_prompt_length", 40)
            clean_prompt = "".join(c if c.isalnum() or c in " -_" else "" for c in prompt[:max_len])
            parts.append(clean_prompt.replace(" ", "_"))

        return out_dir / ("_".join(parts) + ".png")

    def generate(
        self,
        prompt: str,
        lora: str = "vector_flat",
        width: int | None = None,
        height: int | None = None,
        steps: int | None = None,
        guidance: float | None = None,
        seed: int | None = None,
        save_output: bool = True,
    ) -> Image.Image:
        """
        Generate a vector-style graphic.

        Args:
            prompt: Description of the image
            lora: LoRA to use (vector_flat, vector_illustration)
            width: Image width (default: 2400 for print)
            height: Image height (default: 3200 for print)
            steps: Inference steps (default: 30)
            guidance: Guidance scale (default: 7.5)
            seed: Random seed for reproducibility
            save_output: Save to outputs directory

        Returns:
            PIL Image
        """
        # Get preset config
        preset = self.config.get("generation", {}).get("vector_print", {})
        width = width or preset.get("width", 2400)
        height = height or preset.get("height", 3200)
        steps = steps or preset.get("num_inference_steps", 30)
        guidance = guidance or preset.get("guidance_scale", 7.5)

        # Load model and LoRA
        pipe = self.loader.load_txt2img()
        trigger_word, lora_scale = self.loader.load_lora(lora)

        # Build prompt with trigger word
        extra_prompt = preset.get("extra_prompt", "")
        full_prompt = f"{trigger_word}, {prompt}, {extra_prompt}" if trigger_word else f"{prompt}, {extra_prompt}"

        # Negative prompt
        negative = self.config.get("negative_prompts", {}).get("vector", "")

        logger.info(f"Generating: {prompt[:50]}...")
        logger.info(f"Size: {width}x{height}, LoRA: {lora}")

        # Generator for reproducibility
        generator = torch.Generator(device="cpu").manual_seed(seed) if seed is not None else None

        # Generate
        with torch.inference_mode():
            result = pipe(
                prompt=full_prompt,
                negative_prompt=negative,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=guidance,
                generator=generator,
                cross_attention_kwargs={"scale": lora_scale},
            )

        image = result.images[0]

        # Save with DPI metadata
        if save_output:
            output_path = self._get_output_path(prompt, "vector")
            dpi = preset.get("dpi", 300)
            self._save_with_dpi(image, output_path, dpi)
            logger.info(f"Saved: {output_path}")

        return image

    def _save_with_dpi(self, image: Image.Image, path: Path, dpi: int) -> None:
        """Save image with DPI metadata for print."""
        if image.mode == "RGBA":
            bg = Image.new("RGB", image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[3])
            image = bg
        image.save(path, dpi=(dpi, dpi), optimize=True)


class GhibliPipeline:
    """
    Convert photos to Ghibli/anime style using SDXL img2img + LoRA.

    Uses image-to-image transformation to preserve composition
    while applying the anime style.
    """

    STYLE_PROMPTS = {
        "ghibli_style": (
            "Studio Ghibli style, anime, hand-drawn animation, "
            "soft watercolor, vibrant colors, Hayao Miyazaki, masterpiece"
        ),
        "anime_general": (
            "anime style, detailed illustration, pastel colors, "
            "clean lines, beautiful, professional"
        ),
        "vector_flat": (
            "flat illustration, vector art, clean lines, "
            "simple colors, minimalist design"
        ),
    }

    def __init__(self, loader: ModelLoader):
        self.loader = loader
        self.config = loader.config
        self.output_dir = Path(self.config.get("output", {}).get("base_dir", "outputs"))

    def convert(
        self,
        input_image: Image.Image | str,
        style: str = "ghibli_style",
        strength: float | None = None,
        steps: int | None = None,
        guidance: float | None = None,
        seed: int | None = None,
        save_output: bool = True,
        custom_prompt: str | None = None,
    ) -> Image.Image:
        """
        Convert a photo to anime/Ghibli style.

        Args:
            input_image: PIL Image or path to image
            style: LoRA style to apply (ghibli_style, anime_general)
            strength: Transformation strength 0.0-1.0 (default: 0.70)
            steps: Inference steps (default: 35)
            guidance: Guidance scale (default: 7.5)
            seed: Random seed
            save_output: Save to outputs directory
            custom_prompt: Additional prompt text

        Returns:
            Converted PIL Image
        """
        # Load input
        if isinstance(input_image, str):
            input_image = Image.open(input_image).convert("RGB")

        # Get preset
        preset = self.config.get("generation", {}).get("ghibli_transfer", {})
        strength = strength if strength is not None else preset.get("strength", 0.70)
        steps = steps or preset.get("num_inference_steps", 35)
        guidance = guidance or preset.get("guidance_scale", 7.5)

        # Load model and LoRA
        pipe = self.loader.load_img2img()
        trigger_word, lora_scale = self.loader.load_lora(style)

        # Build prompt
        style_prompt = self.STYLE_PROMPTS.get(style, "")
        if custom_prompt:
            prompt = f"{trigger_word}, {custom_prompt}, {style_prompt}"
        else:
            prompt = f"{trigger_word}, {style_prompt}"

        # Negative prompt
        negative = self.config.get("negative_prompts", {}).get("ghibli", "")

        logger.info(f"Converting to {style}...")
        logger.info(f"Strength: {strength}, Steps: {steps}")

        # Resize if too large (SDXL works best at ~1024px)
        original_size = input_image.size
        if max(original_size) > 1536:
            scale = 1536 / max(original_size)
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Resized: {original_size} -> {input_image.size}")

        # Generator
        generator = torch.Generator(device="cpu").manual_seed(seed) if seed is not None else None

        # Convert
        with torch.inference_mode():
            result = pipe(
                prompt=prompt,
                negative_prompt=negative,
                image=input_image,
                strength=strength,
                num_inference_steps=steps,
                guidance_scale=guidance,
                generator=generator,
                cross_attention_kwargs={"scale": lora_scale},
            )

        output = result.images[0]

        # Save
        if save_output:
            out_dir = self.output_dir / "ghibli"
            out_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = out_dir / f"{timestamp}_{style}.png"
            output.save(output_path, optimize=True)
            logger.info(f"Saved: {output_path}")

        return output

    def convert_batch(
        self,
        inputs: list[str],
        style: str = "ghibli_style",
        **kwargs: Any,
    ) -> list[Image.Image]:
        """Convert multiple images."""
        results = []
        for path in inputs:
            try:
                img = self.convert(path, style=style, save_output=True, **kwargs)
                results.append(img)
            except Exception as e:
                logger.error(f"Failed: {path} - {e}")
        return results
