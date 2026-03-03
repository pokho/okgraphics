# OK Print Designs

Local AI-powered print design system for generating vector-style graphics and Ghibli-style image conversions.

## Features

- **Vector Graphics Generation**: Create print-ready graphics at 300 DPI
- **Ghibli Style Transfer**: Convert photos to anime-style illustrations
- **100% Local**: Runs entirely on your VPS, no external APIs
- **Commercial-Friendly Licenses**: Uses models with permissive licenses

## Models Used

| Purpose | Model | License |
|---------|-------|---------|
| Vector Graphics | FLUX.1 [schnell] | Apache 2.0 |
| Vector Graphics (alt) | SD 3.5 Medium | Stability Community |
| Ghibli Style | DreamShaper v8 + LoRA | OpenRAIL |
| Style Transfer | Counterfeit-V3.0 | CreativeML Open RAIL-M |

## Requirements

- Python 3.10+
- CUDA-capable GPU (recommended: 16GB+ VRAM)
- 50GB+ disk space for models

## Quick Start

```bash
# Clone and setup
cd okprintdesigns
python -m venv .venv
source .venv/bin/activate
pip install -e ".[cuda]"

# Download models (first time only)
python scripts/download_models.py

# Start the API server
python -m src.api.server

# Generate a vector graphic
curl -X POST http://localhost:8000/generate/vector \
  -H "Content-Type: application/json" \
  -d '{"prompt": "minimalist mountain landscape", "width": 2400, "height": 3200}'

# Convert photo to Ghibli style
curl -X POST http://localhost:8000/generate/ghibli \
  -F "image=@photo.jpg" \
  -F "prompt=Ghibli style anime version"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate/vector` | POST | Generate vector-style graphic |
| `/generate/ghibli` | POST | Convert image to Ghibli style |
| `/models/list` | GET | List available models |
| `/models/load` | POST | Load a specific model |
| `/health` | GET | Health check |

## Configuration

Edit `configs/config.yaml` to customize:

```yaml
models:
  vector:
    name: "black-forest-labs/FLUX.1-schnell"
    dtype: "float16"
  ghibli:
    name: "Lykon/dreamshaper-8"
    lora: "ghibli-style"

generation:
  vector:
    width: 2400
    height: 3200
    num_inference_steps: 4
    guidance_scale: 0.0
  ghibli:
    strength: 0.75
    num_inference_steps: 30
```

## Project Structure

```
okprintdesigns/
├── src/
│   ├── api/           # FastAPI server
│   ├── models/        # Model loaders
│   ├── pipelines/     # Generation pipelines
│   └── utils/         # Helpers (DPI, resize, etc.)
├── configs/           # Configuration files
├── outputs/           # Generated images
├── scripts/           # Setup and utility scripts
└── docs/              # Documentation
```

## License

Apache 2.0 with Commons Clause - Free for personal and non-commercial use.

For commercial use, please contact us for licensing terms.

**Note:** This license applies to the code only. Model weights (SDXL, LoRAs) have their own licenses - see [docs/LICENSES.md](docs/LICENSES.md).

## Acknowledgments

- [Black Forest Labs](https://blackforestlabs.ai/) for FLUX
- [Stability AI](https://stability.ai/) for Stable Diffusion
- [Lykon](https://huggingface.co/Lykon) for DreamShaper
