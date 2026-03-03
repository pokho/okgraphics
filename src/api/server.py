"""FastAPI server for OK Print Designs - SDXL + LoRA."""

import io
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from PIL import Image
import yaml

from src.models.loaders import ModelLoader
from src.pipelines.vector import VectorPipeline, GhibliPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global instances
model_loader: ModelLoader | None = None
vector_pipeline: VectorPipeline | None = None
ghibli_pipeline: GhibliPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global model_loader, vector_pipeline, ghibli_pipeline

    logger.info("Starting OK Print Designs API...")
    logger.info("Architecture: SDXL + LoRA adapters")
    logger.info("License: OpenRAIL (commercial allowed)")

    model_loader = ModelLoader("configs/config.yaml")
    vector_pipeline = VectorPipeline(model_loader)
    ghibli_pipeline = GhibliPipeline(model_loader)

    logger.info("Ready - models load on first request")

    yield

    logger.info("Shutting down...")
    if model_loader:
        model_loader.clear()


app = FastAPI(
    title="OK Print Designs API",
    description="Local AI print design - SDXL + LoRA",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "model_loaded": model_loader.is_loaded if model_loader else False,
        "current_lora": model_loader.current_lora if model_loader else None,
    }


@app.get("/")
async def root():
    """API info."""
    return {
        "name": "OK Print Designs",
        "version": "0.1.0",
        "architecture": "SDXL + LoRA",
        "license": "OpenRAIL (commercial allowed)",
        "endpoints": {
            "vector": "/generate/vector",
            "ghibli": "/generate/ghibli",
            "loras": "/loras/list",
        },
    }


# --- LoRA Management ---


@app.get("/loras/list")
async def list_loras():
    """List available LoRA styles."""
    if not model_loader:
        raise HTTPException(503, "Not initialized")
    return {"loras": model_loader.list_loras()}


# --- Vector Generation ---


@app.post("/generate/vector")
async def generate_vector(
    prompt: Annotated[str, Form(...)],
    lora: Annotated[str, Form()] = "vector_flat",
    width: Annotated[int, Form()] = 2400,
    height: Annotated[int, Form()] = 3200,
    steps: Annotated[int, Form()] = 30,
    guidance: Annotated[float, Form()] = 7.5,
    seed: Annotated[int | None, Form()] = None,
    return_image: Annotated[bool, Form()] = True,
):
    """
    Generate vector-style graphic for print.

    - **prompt**: Image description
    - **lora**: Style (vector_flat, vector_illustration)
    - **width/height**: Pixels (2400x3200 = 8x10" at 300 DPI)
    - **steps**: Quality (20-40, default 30)
    - **guidance**: Prompt adherence (7.5 default)
    - **seed**: For reproducibility
    """
    if not vector_pipeline:
        raise HTTPException(503, "Pipeline not ready")

    try:
        image = vector_pipeline.generate(
            prompt=prompt,
            lora=lora,
            width=width,
            height=height,
            steps=steps,
            guidance=guidance,
            seed=seed,
            save_output=True,
        )

        if return_image:
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            buf.seek(0)
            return StreamingResponse(buf, media_type="image/png")

        return {"status": "success", "prompt": prompt, "size": f"{width}x{height}", "lora": lora}

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(500, str(e))


# --- Ghibli Style Transfer ---


@app.post("/generate/ghibli")
async def generate_ghibli(
    image: Annotated[UploadFile, File(...)],
    style: Annotated[str, Form()] = "ghibli_style",
    strength: Annotated[float, Form()] = 0.70,
    steps: Annotated[int, Form()] = 35,
    seed: Annotated[int | None, Form()] = None,
    prompt: Annotated[str | None, Form()] = None,
    return_image: Annotated[bool, Form()] = True,
):
    """
    Convert photo to Ghibli/anime style.

    - **image**: Source image file
    - **style**: LoRA style (ghibli_style, anime_general)
    - **strength**: Transform amount (0.5-0.9, default 0.70)
    - **steps**: Quality (25-40, default 35)
    - **seed**: For reproducibility
    - **prompt**: Additional style hints
    """
    if not ghibli_pipeline:
        raise HTTPException(503, "Pipeline not ready")

    try:
        data = await image.read()
        input_img = Image.open(io.BytesIO(data)).convert("RGB")

        output = ghibli_pipeline.convert(
            input_image=input_img,
            style=style,
            strength=strength,
            steps=steps,
            seed=seed,
            custom_prompt=prompt,
            save_output=True,
        )

        if return_image:
            buf = io.BytesIO()
            output.save(buf, format="PNG")
            buf.seek(0)
            return StreamingResponse(buf, media_type="image/png")

        return {"status": "success", "style": style, "strength": strength}

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise HTTPException(500, str(e))


# --- File Access ---


@app.get("/outputs/{category}/{filename}")
async def get_output(category: str, filename: str):
    """Retrieve generated file."""
    path = Path("outputs") / category / filename
    if not path.exists():
        raise HTTPException(404, "Not found")
    return FileResponse(path)


def run():
    """Run the server."""
    config = {}
    config_path = Path("configs/config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)

    app_config = config.get("app", {})
    uvicorn.run(
        "src.api.server:app",
        host=app_config.get("host", "0.0.0.0"),
        port=app_config.get("port", 8000),
        reload=app_config.get("debug", False),
    )


if __name__ == "__main__":
    run()
