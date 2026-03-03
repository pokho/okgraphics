# OK Print Designs

Local AI-powered print design system for generating vector-style graphics and Ghibli-style image conversions using SDXL + LoRA adapters.

## Features

- **Vector Graphics Generation**: Create print-ready graphics at 300 DPI
- **Ghibli Style Transfer**: Convert photos to anime-style illustrations
- **100% Local**: Runs entirely on your machine, no external APIs
- **LoRA Adapters**: Swap styles without loading multiple base models
- **Commercial-Friendly**: SDXL uses OpenRAIL license (commercial allowed)

## Architecture

Single base model (SDXL) with LoRA style adapters:

| Purpose | Base Model | LoRA Adapter |
|---------|------------|--------------|
| Vector Graphics | SDXL Base 1.0 | LineArt / Sticker |
| Ghibli Style | SDXL Base 1.0 | Studio Ghibli Style |
| Anime Style | SDXL Base 1.0 | Pastel Anime |

**Benefits:**
- Only ~6.5 GB base model (vs 40+ GB for multi-model setup)
- Fast style switching (~144 MB per LoRA)
- Lower VRAM requirements

## Requirements

- Python 3.10+
- CUDA-capable GPU (12GB+ VRAM recommended)
- 20GB+ disk space for models

## Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/okgraphics.git
cd okgraphics
python -m venv .venv
source .venv/bin/activate
pip install -e ".[cuda]"

# Download models (first time only)
python scripts/download_models.py

# Generate a vector graphic
python scripts/cli.py generate:vector "minimalist mountain landscape"

# Convert photo to Ghibli style
python scripts/cli.py generate:ghibli photo.jpg --style ghibli_style

# Start the API server
python scripts/cli.py server:start
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `generate:vector <prompt>` | Generate vector-style graphic |
| `generate:ghibli <image>` | Convert image to anime style |
| `server:start` | Start API server |
| `model:list` | List available LoRA adapters |

Run `okgraphics <command> --help` for detailed options.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate/vector` | POST | Generate vector-style graphic |
| `/generate/ghibli` | POST | Convert image to Ghibli style |
| `/loras/list` | GET | List available LoRAs |
| `/health` | GET | Health check |

### Example API Usage

```bash
# Generate vector graphic
curl -X POST http://localhost:8000/generate/vector \
  -F "prompt=minimalist mountain landscape" \
  -F "lora=vector_flat" \
  -F "width=2400" \
  -F "height=3200"

# Convert to Ghibli style
curl -X POST http://localhost:8000/generate/ghibli \
  -F "image=@photo.jpg" \
  -F "style=ghibli_style" \
  -F "strength=0.70"
```

## Configuration

Edit `configs/config.yaml` to customize:

```yaml
# Base model
base_model:
  repo_id: "stabilityai/stable-diffusion-xl-base-1.0"
  dtype: "float16"

# LoRA adapters
loras:
  vector_flat:
    repo_id: "artificialguybr/LineArt-Lora-for-SDXL"
    trigger_word: "line art, vector, flat design"
    scale: 0.85

  ghibli_style:
    repo_id: "artificialguybr/StudioGhibli.Redmond-Style-Lora-For-SDXL"
    trigger_word: "Studio Ghibli style"
    scale: 0.85

# Generation presets
generation:
  vector_print:
    width: 2400   # 8 inches at 300 DPI
    height: 3200  # 10.67 inches at 300 DPI
    num_inference_steps: 30
    guidance_scale: 7.5
    dpi: 300
```

## Project Structure

```
okgraphics/
├── src/
│   ├── api/           # FastAPI server
│   ├── cli/           # Schema-based CLI system
│   ├── commands/      # Command definitions
│   ├── handlers/      # Command implementations
│   ├── models/        # Model loaders
│   ├── pipelines/     # Generation pipelines
│   └── utils/         # Helpers (DPI, resize, etc.)
├── configs/           # Configuration files
├── outputs/           # Generated images
├── scripts/           # Setup and utility scripts
└── docs/              # Documentation
```

## Hardware Requirements

| GPU | VRAM | Performance |
|-----|------|-------------|
| RTX 4090 | 24 GB | ~5 sec/image |
| RTX 3090 | 24 GB | ~7 sec/image |
| RTX 3080 | 10 GB | ~15 sec/image (CPU offload) |

See [docs/HARDWARE.md](docs/HARDWARE.md) for detailed requirements and optimization tips.

## Model Licenses

| Model | License | Commercial Use |
|-------|---------|----------------|
| SDXL Base 1.0 | OpenRAIL | ✅ Yes |
| LineArt LoRA | OpenRAIL | ✅ Yes |
| Ghibli Style LoRA | OpenRAIL | ✅ Yes |

See [docs/LICENSES.md](docs/LICENSES.md) for full details.

## Project License

Apache 2.0 with Commons Clause - Free for personal and non-commercial use.

For commercial use, please contact us for licensing terms.

**Note:** This license applies to the code only. Model weights have their own licenses - see [docs/LICENSES.md](docs/LICENSES.md).

## Acknowledgments

- [Stability AI](https://stability.ai/) for Stable Diffusion XL
- [artificialguybr](https://huggingface.co/artificialguybr) for SDXL LoRA adapters
