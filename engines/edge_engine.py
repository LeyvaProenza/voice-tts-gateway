"""
Motor Microsoft Edge Neural TTS.
Optimizado para locución docente en español y dialectos regionales, con cero consumo de VRAM.
"""

import io
import re
import edge_tts
from pydub import AudioSegment


async def generate_edge_tts_audio(text: str, voice_name: str, speed: float = 0.95, audio_format: str = "mp3") -> bytes:
    """
    Genera audio con Edge-TTS y ajusta la tasa de habla para cadencia educativa.
    Retorna MP3 directamente (sin transcodificación) o WAV según se solicite.
    """
    # Pre-procesar etiquetas de pausa educativa [pausa] o [silencio]
    clean_text = re.sub(r'\[(?:pausa|silencio)\]', '... ', text, flags=re.IGNORECASE)

    # Calcular rate para Edge-TTS (+/- %)
    rate_pct = int(round((speed - 1.0) * 100))
    rate_str = f"{rate_pct:+d}%"

    communicate = edge_tts.Communicate(clean_text, voice_name, rate=rate_str)
    mp3_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_data += chunk["data"]

    if not mp3_data:
        raise ValueError("Edge-TTS no devolvió datos de audio.")

    # Si se solicita MP3, devolver directamente el flujo de Edge-TTS (más rápido y ligero)
    if audio_format.lower() == "mp3":
        return mp3_data

    # Si se solicita WAV, convertir MP3 a WAV en memoria
    audio = AudioSegment.from_file(io.BytesIO(mp3_data), format="mp3")
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    return wav_io.getvalue()
