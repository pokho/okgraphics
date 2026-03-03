# Hardware Requirements

## Minimum Requirements

### For SDXL + LoRA (Recommended Setup)

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | 8 GB | 12 GB+ |
| RAM | 16 GB | 32 GB |
| Storage | 20 GB | 50 GB SSD |
| Python | 3.10+ | 3.11+ |
| CUDA | 11.8+ | 12.1+ |

## Tested Configurations

### NVIDIA RTX 4090 (24 GB VRAM)
- SDXL + LoRA (2400x3200): ~5 sec/image
- Ghibli conversion: ~4 sec/image

### NVIDIA RTX 3090 (24 GB VRAM)
- SDXL + LoRA (2400x3200): ~7 sec/image
- Ghibli conversion: ~5 sec/image

### NVIDIA RTX 3080 (10 GB VRAM)
- SDXL + LoRA: Works with CPU offload - ~15 sec/image
- Ghibli conversion: ~8 sec/image

### NVIDIA RTX 2080 Ti (11 GB VRAM)
- SDXL + LoRA: CPU offload required - ~20 sec/image
- Ghibli conversion: ~10 sec/image

## Cloud VPS Recommendations

### Budget Option (~$0.30-0.80/hr)
- **RunPod**: RTX 3080 / RTX 3090 pods
- **Vast.ai**: RTX 3080 / RTX 3090 rentals
- **Lambda Labs**: RTX 3080 instances

### Performance Option (~$0.80-1.50/hr)
- **RunPod**: RTX 4090 pods
- **Lambda Labs**: RTX 4090 instances
- **Vast.ai**: RTX 4090 rentals

## Memory Optimization Tips

If you have limited VRAM, the system automatically applies these optimizations:

1. **Model CPU Offload**: Moves model weights to RAM when not in use
2. **Attention Slicing**: Reduces memory by processing attention in chunks
3. **VAE Slicing**: Processes VAE one sample at a time
4. **xFormers**: Memory-efficient attention (if installed)

### Manual Configuration

Edit `configs/config.yaml`:

```yaml
hardware:
  device: "cuda"
  memory_fraction: 0.9
  enable_attention_slicing: true
  enable_vae_slicing: true
  enable_xformers: true

base_model:
  enable_model_cpu_offload: true  # Essential for <12GB VRAM
```

## Storage Requirements

| Component | Size |
|-----------|------|
| SDXL Base 1.0 | ~6.5 GB |
| LoRA adapters | ~144 MB each |
| Python env | ~2 GB |

**Total for full setup: ~10 GB**

Compare to multi-model setup:
- FLUX.1-schnell: ~34 GB
- SD 3.5 Medium: ~10 GB
- DreamShaper v8: ~4.2 GB

**SDXL-only saves 40+ GB of disk space.**

## Why SDXL-Only?

| Metric | Multi-Model | SDXL + LoRAs |
|--------|-------------|--------------|
| Disk space | 50+ GB | ~10 GB |
| VRAM needed | 24 GB+ | 8-12 GB |
| Style switching | Load new model (~30s) | Swap LoRA (~1s) |
| Quality | Varies | Consistent |
