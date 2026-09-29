"""
Motores de síntesis de voz para Voice-TTS Gateway:
- Edge-TTS: Microsoft Edge Neural (Español neutro / regional, alta velocidad, 0 VRAM)
- Kokoro-82M: Modelo de IA local en GPU CUDA (Inglés pedagógico, Voice Blending, Español)
- Xiaomi MiMo v2.5: API Cloud con Modo Director y Audio Tags
"""
from .edge_engine import generate_edge_tts_audio
from .kokoro_engine import (
    generate_kokoro_audio,
    get_kokoro_pipeline,
    _kokoro_lock,
    _kokoro_pipelines,
    _kokoro_init_lock,
)
from .mimo_engine import (
    generate_mimo_audio,
    get_mimo_api_key,
)

__all__ = [
    "generate_edge_tts_audio",
    "generate_kokoro_audio",
    "get_kokoro_pipeline",
    "_kokoro_lock",
    "_kokoro_pipelines",
    "_kokoro_init_lock",
    "generate_mimo_audio",
    "get_mimo_api_key",
]
