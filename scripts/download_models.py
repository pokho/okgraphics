#!/usr/bin/env python3
"""Script to download all required models."""

import argparse
import logging
from pathlib import Path

import torch
from huggingface_hub import snapshot_download, login

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Models to download with their license info
MODELS = {
    # Primary models (commercial-friendly licenses)
    "flux-schnell": {
        "repo_id": "black-forest-labs/FLUX.1-schnell",
        "license": "Apache-2.0",
        "commercial": True,
        "size_gb": 34,
        "required": True,
    },
    "dreamshaper": {
        "repo_id": "Lykon/dreamshaper-8",
        "license": "CreativeML-OpenRAIL-M",
        "commercial": True,
        "size_gb": 4.2,
        "required": True,
    },
    # Optional alternative models
    "sd35-medium": {
        "repo_id": "stabilityai/stable-diffusion-3.5-medium",
        "license": "StabilityAI-Community (up to $1M ARR)",
        "commercial": True,
        "size_gb": 10,
        "required": False,
    },
    "counterfeit": {
        "repo_id": "gsdf/Counterfeit-V3.0",
        "license": "CreativeML-OpenRAIL-M",
        "commercial": True,
        "size_gb": 4.2,
        "required": False,
    },
    "sdxl-base": {
        "repo_id": "stabilityai/stable-diffusion-xl-base-1.0",
        "license": "OpenRAIL",
        "commercial": True,
        "size_gb": 6.5,
        "required": False,
    },
}

# LoRA models for specific styles
LORAS = {
    "ghibli-style": {
        "repo_id": "artificialguybr/StudioGhibli.Redmond-Style-Lora-For-SDXL",
        "license": "OpenRAIL",
        "commercial": True,
        "size_mb": 144,
    },
    "line-art": {
        "repo_id": "artificialguybr/LineArt-Lora-for-SDXL",
        "license": "OpenRAIL",
        "commercial": True,
        "size_mb": 144,
    },
}


def download_model(repo_id: str, local_dir: str | None = None) -> Path:
    """Download a model from HuggingFace Hub."""
    logger.info(f"Downloading: {repo_id}")

    kwargs = {"repo_id": repo_id, "local_dir": local_dir}

    path = snapshot_download(**kwargs)
    logger.info(f"Downloaded to: {path}")
    return Path(path)


def estimate_download_size(models: list[str]) -> float:
    """Estimate total download size in GB."""
    total = 0.0
    for name in models:
        if name in MODELS:
            total += MODELS[name]["size_gb"]
        elif name in LORAS:
            total += LORAS[name]["size_mb"] / 1024
    return total


def main():
    parser = argparse.ArgumentParser(description="Download models for OK Print Designs")
    parser.add_argument(
        "--models",
        nargs="+",
        choices=list(MODELS.keys()) + list(LORAS.keys()) + ["all", "required"],
        default=["required"],
        help="Models to download (default: required only)",
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        help="HuggingFace API token for gated models",
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

    # Determine which models to download
    if "all" in args.models:
        to_download = list(MODELS.keys()) + list(LORAS.keys())
    elif "required" in args.models:
        to_download = [k for k, v in MODELS.items() if v.get("required", False)]
    else:
        to_download = args.models

    # Estimate size
    total_size = estimate_download_size(to_download)
    logger.info(f"Models to download: {to_download}")
    logger.info(f"Estimated total size: {total_size:.1f} GB")

    if args.dry_run:
        logger.info("Dry run complete. Run without --dry-run to download.")
        return

    # Download models
    for name in to_download:
        model_info = MODELS.get(name) or LORAS.get(name)
        if not model_info:
            logger.warning(f"Unknown model: {name}")
            continue

        logger.info(f"\n{'=' * 60}")
        logger.info(f"Model: {name}")
        logger.info(f"License: {model_info['license']}")
        logger.info(f"Commercial use: {model_info['commercial']}")
        logger.info(f"{'=' * 60}")

        try:
            download_model(
                model_info["repo_id"],
                local_dir=args.cache_dir,
            )
            logger.info(f"Successfully downloaded: {name}")
        except Exception as e:
            logger.error(f"Failed to download {name}: {e}")

    logger.info("\nDownload complete!")
    logger.info("\nModel License Summary:")
    logger.info("- FLUX.1-schnell: Apache 2.0 (unrestricted commercial use)")
    logger.info("- DreamShaper: CreativeML Open RAIL-M (commercial allowed)")
    logger.info("- SD 3.5 Medium: Stability Community License (commercial up to $1M ARR)")
    logger.info("- Counterfeit-V3.0: CreativeML Open RAIL-M (commercial allowed)")


if __name__ == "__main__":
    main()
