#!/usr/bin/env python3
"""Script to download all required models for OK Print Designs.

Downloads SDXL base model and LoRA adapters.
"""

import argparse
import logging
from pathlib import Path

from huggingface_hub import snapshot_download, login

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Base model
BASE_MODEL = {
    "name": "sdxl-base",
    "repo_id": "stabilityai/stable-diffusion-xl-base-1.0",
    "license": "OpenRAIL",
    "commercial": True,
    "size_gb": 6.5,
    "required": True,
}

# LoRA adapters for different styles
LORAS = {
    "line-art": {
        "repo_id": "artificialguybr/LineArt-Lora-for-SDXL",
        "license": "OpenRAIL",
        "commercial": True,
        "size_mb": 144,
        "description": "Clean line art and vector-style graphics",
    },
    "sticker": {
        "repo_id": "artificialguybr/StickerLoraForSDXL",
        "license": "OpenRAIL",
        "commercial": True,
        "size_mb": 144,
        "description": "Sticker/illustration style",
    },
    "ghibli-style": {
        "repo_id": "artificialguybr/StudioGhibli.Redmond-Style-Lora-For-SDXL",
        "license": "OpenRAIL",
        "commercial": True,
        "size_mb": 144,
        "description": "Studio Ghibli anime style",
    },
    "pastel-anime": {
        "repo_id": "Linaqruf/pastel-anime-style-lora",
        "license": "OpenRAIL",
        "commercial": True,
        "size_mb": 144,
        "description": "General pastel anime aesthetic",
    },
}


def download_model(repo_id: str, local_dir: str | None = None) -> Path:
    """Download a model from HuggingFace Hub."""
    logger.info(f"Downloading: {repo_id}")

    kwargs = {"repo_id": repo_id}
    if local_dir:
        kwargs["local_dir"] = local_dir

    path = snapshot_download(**kwargs)
    logger.info(f"Downloaded to: {path}")
    return Path(path)


def estimate_download_size(include_base: bool, loras: list[str]) -> float:
    """Estimate total download size in GB."""
    total = 0.0
    if include_base:
        total += BASE_MODEL["size_gb"]
    for name in loras:
        if name in LORAS:
            total += LORAS[name]["size_mb"] / 1024
    return total


def main():
    parser = argparse.ArgumentParser(description="Download models for OK Print Designs")
    parser.add_argument(
        "--no-base",
        action="store_true",
        help="Skip base model download (if already cached)",
    )
    parser.add_argument(
        "--loras",
        nargs="+",
        choices=list(LORAS.keys()) + ["all"],
        default=["all"],
        help="LoRA adapters to download (default: all)",
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        help="HuggingFace API token (for gated models)",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        help="Custom cache directory for models",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without downloading",
    )

    args = parser.parse_args()

    # Login if token provided
    if args.hf_token:
        login(token=args.hf_token)
        logger.info("Logged in to HuggingFace Hub")

    # Determine which LoRAs to download
    loras_to_download = list(LORAS.keys()) if "all" in args.loras else args.loras

    # Estimate size
    total_size = estimate_download_size(not args.no_base, loras_to_download)
    logger.info(f"Models to download:")
    if not args.no_base:
        logger.info(f"  - {BASE_MODEL['name']} ({BASE_MODEL['size_gb']} GB)")
    for name in loras_to_download:
        size = LORAS[name]["size_mb"]
        logger.info(f"  - {name} ({size} MB)")
    logger.info(f"Estimated total size: {total_size:.1f} GB")

    if args.dry_run:
        logger.info("Dry run complete. Run without --dry-run to download.")
        return

    # Download base model
    if not args.no_base:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Base Model: {BASE_MODEL['name']}")
        logger.info(f"License: {BASE_MODEL['license']}")
        logger.info(f"Commercial use: {BASE_MODEL['commercial']}")
        logger.info(f"{'=' * 60}")

        try:
            download_model(
                BASE_MODEL["repo_id"],
                local_dir=args.cache_dir,
            )
            logger.info(f"Successfully downloaded: {BASE_MODEL['name']}")
        except Exception as e:
            logger.error(f"Failed to download base model: {e}")
            return

    # Download LoRAs
    for name in loras_to_download:
        lora = LORAS[name]
        logger.info(f"\n{'=' * 60}")
        logger.info(f"LoRA: {name}")
        logger.info(f"Description: {lora['description']}")
        logger.info(f"License: {lora['license']}")
        logger.info(f"{'=' * 60}")

        try:
            download_model(
                lora["repo_id"],
                local_dir=args.cache_dir,
            )
            logger.info(f"Successfully downloaded: {name}")
        except Exception as e:
            logger.error(f"Failed to download {name}: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("Download complete!")
    logger.info("")
    logger.info("Model Summary:")
    logger.info(f"  Base: SDXL 1.0 (OpenRAIL - commercial allowed)")
    logger.info(f"  LoRAs: {len(loras_to_download)} adapters downloaded")
    logger.info("")
    logger.info("Total disk usage: ~%.1f GB", total_size)


if __name__ == "__main__":
    main()
