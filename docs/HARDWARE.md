# Hardware Requirements

## Minimum Requirements

### For FLUX.1-schnell (Vector Graphics)
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | 16 GB | 24 GB+ |
| RAM | 32 GB | 64 GB |
| Storage | 50 GB | 100 GB SSD |
| Python | 3.10+ | 3.11+ |
| CUDA | 11.8+ | 12.1+ |

### For DreamShaper/Counterfeit (Ghibli Style)
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | 8 GB | 12 GB+ |
| RAM | 16 GB | 32 GB |
| Storage | 20 GB | 50 GB SSD |

## Tested Configurations

### NVIDIA RTX 4090 (24 GB VRAM)
- FLUX.1-schnell: Full resolution (2400x3200) - ~8 sec/image
- SD 3.5 Medium: Full resolution - ~15 sec/image
- Ghibli conversion: ~5 sec/image

### NVIDIA RTX 3090 (24 GB VRAM)
- FLUX.1-schnell: Full resolution - ~12 sec/image
- Ghibli conversion: ~7 sec/image

### NVIDIA RTX 3080 (10 GB VRAM)
- FLUX.1-schnell: Requires CPU offload - ~45 sec/image
- Ghibli conversion: Works well - ~10 sec/image

### NVIDIA RTX 2080 Ti (11 GB VRAM)
- FLUX.1-schnell: CPU offload required - ~60 sec/image
- Ghibli conversion: Works - ~12 sec/image

## Cloud VPS Recommendations

### Budget Option (~$0.50-1.00/hr)
- **Lambda Labs**: RTX 3090 / RTX 4090 instances
- **RunPod**: RTX 3090 / RTX 4090 pods
- **Vast.ai**: RTX 3090 / RTX 4090 rentals

### Production Option (~$1.50-3.00/hr)
- **AWS**: p4d.24xlarge (8x A100 40GB)
- **GCP**: a2-highgpu-1g (1x A100 40GB)
- **Lambda Labs**: A100 instances

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

models:
  vector_flux:
    enable_model_cpu_offload: true  # Essential for <24GB VRAM
    enable_sequential_cpu_offload: false  # More aggressive, slower
```

## Storage Requirements

| Model | Size |
|-------|------|
| FLUX.1-schnell | ~34 GB |
| SD 3.5 Medium | ~10 GB |
| DreamShaper v8 | ~4.2 GB |
| Counterfeit-V3.0 | ~4.2 GB |
| SDXL Base | ~6.5 GB |
| LoRA adapters | ~150 MB each |

**Total for all models: ~60 GB**

For minimal setup (FLUX + DreamShaper): **~40 GB**
