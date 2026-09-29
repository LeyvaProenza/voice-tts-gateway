"""
Motor Kokoro-82M TTS acelerado por GPU (NVIDIA CUDA).
Soporta inglés y español experimental, además de mezclas dinámicas de voces (Voice Blending).
"""

import io
import re
import asyncio
import threading
from typing import Dict, Any
from pydub import AudioSegment

_kokoro_pipelines: Dict[str, Any] = {}
_kokoro_lock = asyncio.Lock()
_kokoro_init_lock = threading.Lock()


def get_kokoro_pipeline(lang_code: str = 'a'):
    """Inicialización bajo demanda (Lazy loading) y thread-safe de Kokoro en GPU o CPU."""
    global _kokoro_pipelines
    if lang_code not in _kokoro_pipelines:
        with _kokoro_init_lock:
            if lang_code not in _kokoro_pipelines:
                import torch
                from kokoro import KPipeline
                device = "cuda" if torch.cuda.is_available() else "cpu"
                print(f"Inicializando Kokoro KPipeline (lang='{lang_code}', device='{device}')...")
                _kokoro_pipelines[lang_code] = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M', device=device)
    return _kokoro_pipelines[lang_code]


def generate_kokoro_audio(text: str, voice: str, speed: float = 0.95, audio_format: str = "mp3") -> bytes:
    """
    Genera audio con Kokoro-82M a 24000 Hz. Exporta en MP3 (192kbps) o WAV 16-bit.
    Soporta voces individuales y mezclas separadas por comas (ej. 'af_bella,af_sarah' o 'ef_dora,af_sarah').
    """
    import torch
    import soundfile as sf
    import numpy as np

    # Pre-procesar pausas para guiones
    clean_text = re.sub(r'\[(?:pausa|pause|silence)\]', '... ', text, flags=re.IGNORECASE)

    # Limpiar y normalizar lista de voces para soportar mezclas arbitrarias con o sin espacios
    cleaned_voices = ",".join(v.strip() for v in voice.split(",") if v.strip())
    first_voice = cleaned_voices.split(",")[0] if cleaned_voices else "af_heart"

    # Detectar si la voz es en español ('e'), británica ('b') o americana ('a')
    if first_voice.startswith(('ef_', 'em_')) or any(v.strip().startswith(('ef_', 'em_')) for v in cleaned_voices.split(',')):
        lang_code = 'e'
    elif first_voice.startswith('b'):
        lang_code = 'b'
    else:
        lang_code = 'a'

    pipeline = get_kokoro_pipeline(lang_code)

    generator = pipeline(clean_text, voice=cleaned_voices, speed=speed, split_pattern=r'\n+')
    audio_chunks = []
    for _, _, audio in generator:
        if audio is not None:
            audio_chunks.append(audio)

    if not audio_chunks:
        raise ValueError("Kokoro no devolvió datos de audio.")

    full_audio = torch.cat(
        [torch.from_numpy(c) if not isinstance(c, torch.Tensor) else c for c in audio_chunks],
        dim=0
    ).numpy()

    # Si se solicita MP3, convertir PCM a MP3 a 192 kbps
    if audio_format.lower() == "mp3":
        # Escalar de float [-1.0, 1.0] a int16
        audio_int16 = (np.clip(full_audio, -1.0, 1.0) * 32767).astype(np.int16)
        audio_seg = AudioSegment(
            audio_int16.tobytes(),
            frame_rate=24000,
            sample_width=2,
            channels=1
        )
        mp3_io = io.BytesIO()
        audio_seg.export(mp3_io, format="mp3", bitrate="192k")
        return mp3_io.getvalue()

    # Si se solicita WAV
    wav_io = io.BytesIO()
    sf.write(wav_io, full_audio, 24000, format='WAV', subtype='PCM_16')
    return wav_io.getvalue()
