"""Utility functions for image processing and DPI handling."""

import math
from pathlib import Path
from typing import Tuple

from PIL import Image


def calculate_dimensions_for_dpi(
    inches_width: float,
    inches_height: float,
    dpi: int = 300,
) -> Tuple[int, int]:
    """
    Calculate pixel dimensions for a given physical size at a specific DPI.

    Args:
        inches_width: Width in inches
        inches_height: Height in inches
        dpi: Dots per inch

    Returns:
        Tuple of (width, height) in pixels

    Example:
        >>> calculate_dimensions_for_dpi(8, 10, 300)
        (2400, 3000)
    """
    width = int(inches_width * dpi)
    height = int(inches_height * dpi)
    return width, height


def calculate_inches_from_pixels(
    pixels_width: int,
    pixels_height: int,
    dpi: int = 300,
) -> Tuple[float, float]:
    """
    Calculate physical dimensions from pixel dimensions.

    Args:
        pixels_width: Width in pixels
        pixels_height: Height in pixels
        dpi: Dots per inch

    Returns:
        Tuple of (width, height) in inches
    """
    inches_width = pixels_width / dpi
    inches_height = pixels_height / dpi
    return inches_width, inches_height


def resize_for_print(
    image: Image.Image,
    target_width_inches: float,
    target_height_inches: float,
    dpi: int = 300,
    resample: Image.Resampling = Image.Resampling.LANCZOS,
) -> Image.Image:
    """
    Resize an image to specific print dimensions at a given DPI.

    Args:
        image: PIL Image to resize
        target_width_inches: Target width in inches
        target_height_inches: Target height in inches
        dpi: Target DPI
        resample: Resampling method

    Returns:
        Resized PIL Image
    """
    new_width, new_height = calculate_dimensions_for_dpi(
        target_width_inches, target_height_inches, dpi
    )
    return image.resize((new_width, new_height), resample)


def save_for_print(
    image: Image.Image,
    output_path: str | Path,
    dpi: int = 300,
    format: str = "PNG",
    quality: int = 95,
) -> Path:
    """
    Save an image with print-ready DPI metadata.

    Args:
        image: PIL Image to save
        output_path: Where to save the file
        dpi: DPI to embed in metadata
        format: Output format (PNG, JPEG, TIFF)
        quality: Quality for JPEG format

    Returns:
        Path to saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert RGBA to RGB for JPEG
    if format.upper() == "JPEG" and image.mode == "RGBA":
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background

    save_kwargs = {"dpi": (dpi, dpi)}

    if format.upper() == "JPEG":
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif format.upper() == "PNG":
        save_kwargs["optimize"] = True
    elif format.upper() == "TIFF":
        save_kwargs["compression"] = "lzw"

    image.save(output_path, format=format, **save_kwargs)
    return output_path


# Common print size presets (in inches)
PRINT_SIZES = {
    # Standard photo sizes
    "4x6": (4, 6),
    "5x7": (5, 7),
    "8x10": (8, 10),
    "11x14": (11, 14),
    # Paper sizes
    "letter": (8.5, 11),
    "a4": (8.27, 11.69),
    "a3": (11.69, 16.54),
    "a2": (16.54, 23.39),
    # Poster sizes
    "poster_small": (11, 17),
    "poster_medium": (18, 24),
    "poster_large": (24, 36),
    # Square formats
    "square_small": (8, 8),
    "square_medium": (12, 12),
    "square_large": (18, 18),
}


def get_print_size_pixels(size_name: str, dpi: int = 300) -> Tuple[int, int]:
    """
    Get pixel dimensions for a named print size.

    Args:
        size_name: Name of the print size (e.g., "letter", "a4", "8x10")
        dpi: Dots per inch

    Returns:
        Tuple of (width, height) in pixels
    """
    if size_name not in PRINT_SIZES:
        raise ValueError(
            f"Unknown size: {size_name}. Available: {list(PRINT_SIZES.keys())}"
        )

    inches = PRINT_SIZES[size_name]
    return calculate_dimensions_for_dpi(inches[0], inches[1], dpi)


def maintain_aspect_ratio(
    original_size: Tuple[int, int],
    target_width: int | None = None,
    target_height: int | None = None,
) -> Tuple[int, int]:
    """
    Calculate new dimensions maintaining aspect ratio.

    Args:
        original_size: Original (width, height)
        target_width: Target width (if specified)
        target_height: Target height (if specified)

    Returns:
        New (width, height) maintaining aspect ratio
    """
    orig_w, orig_h = original_size
    aspect = orig_w / orig_h

    if target_width is not None and target_height is not None:
        # Both specified - fit within bounds
        target_aspect = target_width / target_height
        if aspect > target_aspect:
            # Width-limited
            new_width = target_width
            new_height = int(target_width / aspect)
        else:
            # Height-limited
            new_height = target_height
            new_width = int(target_height * aspect)
    elif target_width is not None:
        new_width = target_width
        new_height = int(target_width / aspect)
    elif target_height is not None:
        new_height = target_height
        new_width = int(target_height * aspect)
    else:
        return original_size

    return (new_width, new_height)
