"""
Voice-TTS Gateway - Servidor Local de Locución y Síntesis de Voz Educativa.
Integra:
- Microsoft Edge Neural TTS (Español neutro / regional, alta velocidad, 0 VRAM)
- Kokoro-82M AI con aceleración GPU CUDA (Inglés pedagógico, Voice Blending, Español)
- Xiaomi MiMo Speech Synthesis v2.5 (Modo Director y Audio Tags en la Nube)
- Motor de Sincronización y Doblaje de Subtítulos (.SRT / .VTT)
"""

import os
import re
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pydantic import BaseModel, Field

# Re-exportaciones e importaciones de módulos desacoplados
from catalog import VOICES_CATALOG, KOKORO_VOICES, MIMO_VOICES
from engines.edge_engine import generate_edge_tts_audio
from engines.kokoro_engine import (
    generate_kokoro_audio,
    get_kokoro_pipeline,
    _kokoro_lock,
    _kokoro_pipelines,
    _kokoro_init_lock,
)
from engines.mimo_engine import generate_mimo_audio, get_mimo_api_key
from subtitles import (
    parse_subtitles,
    synthesize_text_segment,
    generate_synced_subtitle_audio,
    generate_continuous_subtitle_audio,
    MAX_SUBTITLE_FILE_SIZE,
)

# Directorios de trabajo
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "output")
SPEAKERS_DIR = os.path.join(WORKSPACE_DIR, "speakers")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SPEAKERS_DIR, exist_ok=True)


def load_env():
    """Carga variables del archivo .env si existen."""
    env_file = os.path.join(WORKSPACE_DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if k and k not in os.environ:
                        os.environ[k] = v


load_env()

# Inicialización de FastAPI
app = FastAPI(
    title="Voice-TTS Educational Gateway",
    description="Servidor local de narración pedagógica y síntesis de voz (Edge-TTS para Español + Kokoro-82M con GPU para Inglés + MiMo v2.5).",
    version="3.1.0",
)

# Enable CORS for external agents and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================================
#  API Endpoints
# =========================================================================

@app.get("/api/voices")
def get_voices():
    """Devuelve la lista curada de voces disponibles en español e inglés."""
    return VOICES_CATALOG


@app.get("/api/status")
def get_status():
    """Estado general del servidor y detección de aceleración por GPU."""
    try:
        import torch
        cuda_ok = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_ok else "CPU"
    except Exception:
        cuda_ok = False
        device_name = "CPU"

    mimo_active = bool(get_mimo_api_key())

    return {
        "status": "connected",
        "gpu_available": cuda_ok,
        "device": device_name,
        "default_format": "mp3",
        "supported_formats": ["mp3", "wav"],
        "engines": {
            "spanish": "Microsoft Edge Neural (Alta velocidad, 0 VRAM)",
            "english": "Kokoro-82M (Acelerado por GPU CUDA)",
            "mimo": "Xiaomi MiMo v2.5 (Modo Director y Emociones en la Nube)" if mimo_active else "Inactivo (MIMO_API_KEY no detectada)"
        }
    }


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None          # Ej: "es-MX-JorgeNeural", "af_heart" o "mimo-Chloe"
    speaker_wav: Optional[str] = None    # Compatibilidad previa ("es-MX-JorgeNeural.wav")
    language: Optional[str] = None       # "es" o "en"
    speed: Optional[float] = Field(default=0.95, ge=0.25, le=3.0)  # 0.95x = Ritmo pedagógico recomendado
    format: Optional[str] = "mp3"        # "mp3" (recomendado, ~10x más ligero) o "wav"
    style_prompt: Optional[str] = None   # Instrucciones de tono/emoción para Xiaomi MiMo (Modo Director)
    # Compatibilidad previa para parámetros de XTTS (no requeridos pero tolerados)
    temperature: Optional[float] = None
    length_penalty: Optional[float] = None
    repetition_penalty: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    remove_ceceo: Optional[bool] = None


@app.post("/api/tts")
async def tts_generate(req: TTSRequest):
    """
    Endpoint unificado de síntesis de voz:
    - Xiaomi MiMo: Si la voz es MiMo o prefijo 'mimo-'.
    - Kokoro-82M: Si la voz es Kokoro o idioma 'en' o mezclas.
    - Edge Neural: Si la voz es de Edge-TTS o idioma 'es'.
    Retorna el stream binario de audio en formato MP3 o WAV.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="El campo 'text' no puede estar vacío.")

    # Resolver el identificador de voz
    voice_id = req.voice.strip() if req.voice else None
    if not voice_id and req.speaker_wav:
        voice_clean = req.speaker_wav.strip()
        voice_id = voice_clean[:-4] if voice_clean.lower().endswith(".wav") else voice_clean

    # Si aún no hay voz, asignar por omisión según el idioma
    lang = (req.language or "").lower().strip()
    if not voice_id:
        voice_id = "af_heart" if lang == "en" else "es-MX-JorgeNeural"

    speed = req.speed if req.speed is not None else 0.95

    # Determinar formato de salida (mp3 por omisión)
    audio_format = (req.format or "mp3").lower().strip()
    if audio_format not in ["mp3", "wav"]:
        audio_format = "mp3"

    media_type = "audio/mpeg" if audio_format == "mp3" else "audio/wav"

    # 1. Caso Xiaomi MiMo (Cloud con Modo Director y Emociones)
    is_mimo = (
        voice_id in MIMO_VOICES
        or voice_id.lower().startswith("mimo-")
        or voice_id.lower().startswith("mimo_")
        or voice_id.lower() in ["chloe", "mia", "milo", "dean", "mimo_default"]
    )
    if is_mimo:
        try:
            print(f"[TTS] Sintetizando con Xiaomi MiMo Cloud (Voz: {voice_id}, Speed: {speed}, Format: {audio_format}, Style: {req.style_prompt})...")
            audio_bytes = await asyncio.to_thread(generate_mimo_audio, req.text, voice_id, speed, audio_format, req.style_prompt)
            safe_filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', voice_id)
            return Response(
                content=audio_bytes,
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={safe_filename}_output.{audio_format}"},
            )
        except Exception as e:
            print(f"[TTS Error MiMo]: {e}")
            raise HTTPException(status_code=500, detail=f"Error en motor Xiaomi MiMo: {str(e)}")

    # 2. Caso Kokoro (Inglés, Español con Kokoro y Mezclas de Voces)
    is_kokoro = (
        voice_id in KOKORO_VOICES
        or lang == "en"
        or voice_id.startswith(("af_", "am_", "bf_", "bm_", "ef_", "em_"))
        or ("," in voice_id and any(v.strip().startswith(("af_", "am_", "bf_", "bm_", "ef_", "em_")) for v in voice_id.split(",")))
    )
    if is_kokoro:
        try:
            print(f"[TTS] Sintetizando con Kokoro-82M (Voz: {voice_id}, Speed: {speed}, Format: {audio_format})...")
            async with _kokoro_lock:
                audio_bytes = await asyncio.to_thread(generate_kokoro_audio, req.text, voice_id, speed, audio_format)
            safe_filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', voice_id)
            return Response(
                content=audio_bytes,
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={safe_filename}_output.{audio_format}"},
            )
        except Exception as e:
            print(f"[TTS Error Kokoro]: {e}")
            raise HTTPException(status_code=500, detail=f"Error en motor Kokoro: {str(e)}")

    # 3. Caso Edge Neural (Español u otras voces Microsoft)
    try:
        print(f"[TTS] Sintetizando con Edge Neural (Voz: {voice_id}, Speed: {speed}, Format: {audio_format})...")
        audio_bytes = await generate_edge_tts_audio(req.text, voice_id, speed, audio_format)
        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={voice_id}_output.{audio_format}"},
        )
    except Exception as e:
        print(f"[TTS Error Edge]: {e}")
        raise HTTPException(status_code=500, detail=f"Error en motor Edge-TTS: {str(e)}")


class SubtitleTTSRequest(BaseModel):
    subtitle_text: str
    voice: Optional[str] = None          # Ej: "es-MX-JorgeNeural", "af_heart", "mimo-Chloe"
    language: Optional[str] = None       # "es" o "en"
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=3.0)         # Velocidad base de locución
    mode: Optional[str] = "synced"       # "synced" (alineado a timestamps) o "continuous" (audiolibro corrido)
    format: Optional[str] = "mp3"        # "mp3" o "wav"
    style_prompt: Optional[str] = None   # Estilo/emoción para Xiaomi MiMo
    max_speed_factor: Optional[float] = Field(default=1.35, ge=1.0, le=2.5) # Límite de aceleración si la frase excede la ventana


@app.post("/api/tts/subtitle")
async def tts_subtitle_json(req: SubtitleTTSRequest):
    """
    Convierte subtítulos (SRT o WebVTT) provistos como texto JSON a audio.
    Soporta:
    - Modo 'synced': Monta las frases en los timestamps exactos con silencios y time-stretch preventivo.
    - Modo 'continuous': Extrae el texto limpio y sintetiza una narración fluida y corrida.
    """
    if not req.subtitle_text or not req.subtitle_text.strip():
        raise HTTPException(status_code=400, detail="El contenido de 'subtitle_text' no puede estar vacío.")

    parsed = parse_subtitles(req.subtitle_text)
    if not parsed:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron subtítulos válidos. Verifica el formato SRT (00:00:01,000 --> 00:00:04,000) o WebVTT."
        )

    # Resolver voz
    voice_id = req.voice.strip() if req.voice else None
    lang = (req.language or "").lower().strip()
    if not voice_id:
        voice_id = "af_heart" if lang == "en" else "es-MX-JorgeNeural"

    speed = req.speed if req.speed is not None else 1.0
    audio_format = (req.format or "mp3").lower().strip()
    if audio_format not in ["mp3", "wav"]:
        audio_format = "mp3"
    media_type = "audio/mpeg" if audio_format == "mp3" else "audio/wav"

    mode = (req.mode or "synced").lower().strip()
    max_speed = req.max_speed_factor if req.max_speed_factor is not None else 1.35

    try:
        print(f"[TTS Subtitle] Procesando {len(parsed)} subtítulos (Modo: {mode}, Voz: {voice_id}, Formato: {audio_format})...")
        if mode == "continuous":
            audio_bytes = await generate_continuous_subtitle_audio(
                parsed, voice_id, speed=speed, audio_format=audio_format, style_prompt=req.style_prompt
            )
        else:
            audio_bytes = await generate_synced_subtitle_audio(
                parsed, voice_id, speed=speed, audio_format=audio_format, style_prompt=req.style_prompt, max_speed_factor=max_speed
            )

        safe_filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', voice_id)
        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=subtitles_{mode}_{safe_filename}.{audio_format}",
                "X-Subtitle-Count": str(len(parsed))
            }
        )
    except Exception as e:
        print(f"[TTS Subtitle Error]: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando subtítulos: {str(e)}")


@app.post("/api/tts/subtitle/file")
async def tts_subtitle_file(
    file: UploadFile = File(...),
    voice: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    speed: Optional[float] = Form(1.0),
    mode: Optional[str] = Form("synced"),
    format: Optional[str] = Form("mp3"),
    style_prompt: Optional[str] = Form(None),
    max_speed_factor: Optional[float] = Form(1.35)
):
    """
    Recibe un archivo de subtítulos (.srt o .vtt) mediante subida de formulario
    y devuelve la pista de audio generada (sincronizada o continua).
    """
    raw_content = await file.read()
    if len(raw_content) > MAX_SUBTITLE_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo de subtítulos supera el límite de {MAX_SUBTITLE_FILE_SIZE // (1024 * 1024)} MB."
        )
    try:
        text_content = raw_content.decode("utf-8")
    except UnicodeDecodeError:
        text_content = raw_content.decode("latin-1", errors="replace")

    req = SubtitleTTSRequest(
        subtitle_text=text_content,
        voice=voice,
        language=language,
        speed=speed,
        mode=mode,
        format=format,
        style_prompt=style_prompt,
        max_speed_factor=max_speed_factor
    )
    return await tts_subtitle_json(req)


# =========================================================================
#  Endpoints de Compatibilidad Silenciosa (Para llamadas heredadas)
# =========================================================================

@app.get("/api/speakers")
def get_legacy_speakers():
    """Devuelve las voces en formato compatible con llamadas previas."""
    all_voices = []
    for lang, voices in VOICES_CATALOG.items():
        for v in voices:
            all_voices.append({"name": f"{v['id']}.wav", "size_kb": 100})
    return {"speakers": all_voices}

@app.post("/api/server/start")
def dummy_start_server():
    return {"success": True, "message": "Motores Edge-TTS, Kokoro y MiMo listos para síntesis."}

@app.post("/api/server/stop")
def dummy_stop_server():
    return {"success": True, "message": "Servidores en modo espera."}

@app.get("/api/server/log")
def dummy_server_log():
    return {"log": "Servidor activo en modo producción educativa.", "exists": True}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

# =========================================================================
#  Static Files (Frontend UI)
# =========================================================================
app.mount("/", StaticFiles(directory=os.path.join(WORKSPACE_DIR, "static"), html=True), name="static")
