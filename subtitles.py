"""
Módulo de Procesamiento y Doblaje de Subtítulos (.SRT / .VTT) a Audio.
Permite convertir archivos de subtítulos en:
- Pistas de audio perfectamente sincronizadas con marcas de tiempo (Modo 'synced').
- Narraciones fluidas corridas estilo audiolibro (Modo 'continuous').
"""

import io
import re
import asyncio
from typing import Optional, Dict, Any, List
from pydub import AudioSegment
from pydub.effects import speedup

from catalog import KOKORO_VOICES, MIMO_VOICES
from engines.edge_engine import generate_edge_tts_audio
from engines.kokoro_engine import generate_kokoro_audio, _kokoro_lock
from engines.mimo_engine import generate_mimo_audio

MAX_SUBTITLE_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def parse_subtitles(content: str) -> List[Dict[str, Any]]:
    """
    Parsea texto de subtítulos en formato SRT o WebVTT a una lista de diccionarios:
    [{"index": int, "start_ms": int, "end_ms": int, "duration_ms": int, "text": str}]
    Limpia etiquetas HTML (<font>, <i>, <b>), estilos CSS y marcas de formato SSA/VTT.
    Ordena cronológicamente los segmentos y normaliza la numeración.
    """
    text = content.replace("\r\n", "\n").replace("\r", "\n").strip()

    # Si es WebVTT, descartar encabezado
    if text.startswith("WEBVTT"):
        lines = text.split("\n")
        idx = 0
        while idx < len(lines) and lines[idx].strip():
            idx += 1
        text = "\n".join(lines[idx:]).strip()

    # Regex para extraer marcas de tiempo: (HH:)?MM:SS[,.]mmm --> (HH:)?MM:SS[,.]mmm
    time_pat = re.compile(
        r'(?:(?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{3}))\s*-->\s*(?:(?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{3}))'
    )

    def to_ms(h, m, s, ms) -> int:
        hours = int(h) if h else 0
        minutes = int(m)
        seconds = int(s)
        millis = int(ms)
        return hours * 3600000 + minutes * 60000 + seconds * 1000 + millis

    blocks = re.split(r'\n\s*\n', text)
    subtitles = []
    item_index = 1

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n")
        time_match = None
        time_line_idx = -1

        for i, line in enumerate(lines):
            m = time_pat.search(line)
            if m:
                time_match = m
                time_line_idx = i
                break

        if not time_match:
            continue

        h1, m1, s1, ms1, h2, m2, s2, ms2 = time_match.groups()
        start_ms = to_ms(h1, m1, s1, ms1)
        end_ms = to_ms(h2, m2, s2, ms2)

        raw_text_lines = lines[time_line_idx + 1:]
        raw_text = " ".join(raw_text_lines).strip()

        # Limpiar etiquetas HTML y formato (ej: <i>, <b>, <font...>, <c.color>)
        clean_text = re.sub(r'<[^>]+>', '', raw_text)
        # Limpiar llaves SSA/ASS ej {\an8}
        clean_text = re.sub(r'\{[^}]+\}', '', clean_text)
        # Normalizar espacios
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        if clean_text and end_ms > start_ms:
            subtitles.append({
                "index": item_index,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "duration_ms": end_ms - start_ms,
                "text": clean_text
            })
            item_index += 1

    # Ordenar cronológicamente por start_ms y end_ms, y reindexar
    subtitles.sort(key=lambda s: (s["start_ms"], s["end_ms"]))
    for i, s in enumerate(subtitles):
        s["index"] = i + 1

    return subtitles


async def synthesize_text_segment(text: str, voice_id: str, speed: float = 1.0, style_prompt: Optional[str] = None) -> AudioSegment:
    """
    Sintetiza un fragmento individual de texto con el motor adecuado (MiMo, Kokoro o Edge)
    y lo retorna como un AudioSegment en memoria.
    """
    is_mimo = (
        voice_id in MIMO_VOICES
        or voice_id.lower().startswith("mimo-")
        or voice_id.lower().startswith("mimo_")
        or voice_id.lower() in ["chloe", "mia", "milo", "dean", "mimo_default"]
    )
    if is_mimo:
        wav_bytes = await asyncio.to_thread(generate_mimo_audio, text, voice_id, speed, "wav", style_prompt)
        return AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")

    is_kokoro = (
        voice_id in KOKORO_VOICES
        or voice_id.startswith(("af_", "am_", "bf_", "bm_", "ef_", "em_"))
        or ("," in voice_id and any(v.strip().startswith(("af_", "am_", "bf_", "bm_", "ef_", "em_")) for v in voice_id.split(",")))
    )
    if is_kokoro:
        async with _kokoro_lock:
            wav_bytes = await asyncio.to_thread(generate_kokoro_audio, text, voice_id, speed, "wav")
        return AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")

    # Edge-TTS por omisión
    wav_bytes = await generate_edge_tts_audio(text, voice_id, speed, "wav")
    return AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")


async def generate_synced_subtitle_audio(
    subtitles: List[Dict[str, Any]],
    voice_id: str,
    speed: float = 1.0,
    audio_format: str = "mp3",
    style_prompt: Optional[str] = None,
    max_speed_factor: float = 1.35
) -> bytes:
    """
    Construye una pista de audio perfectamente alineada temporalmente con los subtítulos:
    - Inserta silencios en los espacios vacíos.
    - Si una frase excede la ventana disponible antes del siguiente subtítulo, aplica time-stretch (speedup).
    - Coloca cada segmento en su marca de tiempo exacta (start_ms).
    """
    if not subtitles:
        raise ValueError("No se encontraron subtítulos válidos para procesar.")

    total_duration_ms = subtitles[-1]["end_ms"] + 1000
    master_track = AudioSegment.silent(duration=total_duration_ms, frame_rate=24000)

    for i, sub in enumerate(subtitles):
        text = sub["text"]
        start_ms = sub["start_ms"]
        end_ms = sub["end_ms"]

        # Determinar ventana máxima antes de que comience el siguiente subtítulo
        if i + 1 < len(subtitles):
            next_start = subtitles[i + 1]["start_ms"]
            available_ms = next_start - start_ms
        else:
            available_ms = end_ms - start_ms + 1000

        seg_audio = await synthesize_text_segment(text, voice_id, speed=speed, style_prompt=style_prompt)
        duration_ms = len(seg_audio)

        # Ajuste dinámico de velocidad si la voz sobrepasa el intervalo disponible
        if duration_ms > available_ms and available_ms > 400:
            ratio = duration_ms / available_ms
            capped_ratio = min(ratio, max_speed_factor)
            try:
                seg_audio = speedup(seg_audio, playback_speed=capped_ratio)
                duration_ms = len(seg_audio)
            except Exception as speed_err:
                print(f"[Subtitle Dubbing] Advertencia al acelerar segmento {sub['index']}: {speed_err}")

        # Expandir la pista maestra si el segmento excede la duración estimada
        if start_ms + duration_ms > len(master_track):
            extra = (start_ms + duration_ms) - len(master_track) + 500
            master_track += AudioSegment.silent(duration=extra, frame_rate=24000)

        master_track = master_track.overlay(seg_audio, position=start_ms)

    # Exportar a formato solicitado
    out_io = io.BytesIO()
    if audio_format.lower() == "wav":
        master_track.export(out_io, format="wav")
    else:
        master_track.export(out_io, format="mp3", bitrate="192k")

    return out_io.getvalue()


async def generate_continuous_subtitle_audio(
    subtitles: List[Dict[str, Any]],
    voice_id: str,
    speed: float = 0.95,
    audio_format: str = "mp3",
    style_prompt: Optional[str] = None
) -> bytes:
    """
    Une todos los subtítulos en un texto fluido con pausas naturales entre oraciones
    y sintetiza una narración continua (estilo audiolibro).
    """
    if not subtitles:
        raise ValueError("No se encontraron subtítulos válidos para procesar.")

    joined_text = " ... ".join(s["text"] for s in subtitles)

    is_mimo = (
        voice_id in MIMO_VOICES
        or voice_id.lower().startswith("mimo-")
        or voice_id.lower().startswith("mimo_")
        or voice_id.lower() in ["chloe", "mia", "milo", "dean", "mimo_default"]
    )
    if is_mimo:
        return await asyncio.to_thread(generate_mimo_audio, joined_text, voice_id, speed, audio_format, style_prompt)

    is_kokoro = (
        voice_id in KOKORO_VOICES
        or voice_id.startswith(("af_", "am_", "bf_", "bm_", "ef_", "em_"))
        or ("," in voice_id and any(v.strip().startswith(("af_", "am_", "bf_", "bm_", "ef_", "em_")) for v in voice_id.split(",")))
    )
    if is_kokoro:
        async with _kokoro_lock:
            return await asyncio.to_thread(generate_kokoro_audio, joined_text, voice_id, speed, audio_format)

    return await generate_edge_tts_audio(joined_text, voice_id, speed, audio_format)
