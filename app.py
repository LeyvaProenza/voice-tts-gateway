import os
import sys
import io
import re
import asyncio
from typing import Optional, Dict, Any, List
import requests
import edge_tts
from pydub import AudioSegment
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

app = FastAPI(
    title="Voice-TTS Educational Gateway",
    description="Servidor local de narración pedagógica y síntesis de voz (Edge-TTS para Español + Kokoro-82M con GPU para Inglés).",
    version="3.0.0",
)

# Enable CORS for external agents and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "output")
SPEAKERS_DIR = os.path.join(WORKSPACE_DIR, "speakers")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SPEAKERS_DIR, exist_ok=True)

# =========================================================================
#  Catálogo Curado de Voces Educativas
# =========================================================================

VOICES_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "es": [
        {
            "id": "es-MX-JorgeNeural",
            "name": "Jorge (Recomendado)",
            "gender": "Masculino",
            "accent": "México",
            "category": "Latinoamérica",
            "recommended": True,
            "description": "Tono sereno, cálido y explicativo. Dicción impecable para docencia y tutoriales.",
            "engine": "edge-tts"
        },
        {
            "id": "es-MX-DaliaNeural",
            "name": "Dalia (Recomendada)",
            "gender": "Femenino",
            "accent": "México",
            "category": "Latinoamérica",
            "recommended": True,
            "description": "Voz clara, empática y natural, excelente para exposiciones y material formativo.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CO-GonzaloNeural",
            "name": "Gonzalo",
            "gender": "Masculino",
            "accent": "Colombia",
            "category": "Latinoamérica",
            "recommended": False,
            "description": "Acento neutro y formal, ideal para lecturas académicas o científicas.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CO-SalomeNeural",
            "name": "Salomé",
            "gender": "Femenino",
            "accent": "Colombia",
            "category": "Latinoamérica",
            "recommended": False,
            "description": "Tono pausado y suave, muy adecuado para audiolibros educativos.",
            "engine": "edge-tts"
        },
        {
            "id": "es-AR-TomasNeural",
            "name": "Tomás",
            "gender": "Masculino",
            "accent": "Argentina",
            "category": "Latinoamérica",
            "recommended": False,
            "description": "Locución segura y profesional.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CL-CatalinaNeural",
            "name": "Catalina",
            "gender": "Femenino",
            "accent": "Chile",
            "category": "Latinoamérica",
            "recommended": False,
            "description": "Voz limpia, expresiva y didáctica.",
            "engine": "edge-tts"
        },
        {
            "id": "es-US-AlonsoNeural",
            "name": "Alonso",
            "gender": "Masculino",
            "accent": "Latino Neutro (EE.UU.)",
            "category": "Latinoamérica",
            "recommended": False,
            "description": "Locución dinámica y articulada para presentaciones corporativas.",
            "engine": "edge-tts"
        },
        {
            "id": "es-US-PalomaNeural",
            "name": "Paloma",
            "gender": "Femenino",
            "accent": "Latino Neutro (EE.UU.)",
            "category": "Latinoamérica",
            "recommended": False,
            "description": "Tono joven, fresco y claro.",
            "engine": "edge-tts"
        },
        {
            "id": "es-ES-AlvaroNeural",
            "name": "Álvaro",
            "gender": "Masculino",
            "accent": "España",
            "category": "Castellano (España)",
            "recommended": False,
            "description": "Acento castellano formal y bien articulado.",
            "engine": "edge-tts"
        },
        {
            "id": "es-ES-ElviraNeural",
            "name": "Elvira",
            "gender": "Femenino",
            "accent": "España",
            "category": "Castellano (España)",
            "recommended": False,
            "description": "Acento castellano clásico y sereno.",
            "engine": "edge-tts"
        },
    ],
    "en": [
        # --- MEZCLAS EDUCATIVAS (VOICE BLENDING) ---
        {
            "id": "af_bella,af_sarah",
            "name": "Bella & Sarah (Mezcla Educativa)",
            "gender": "Femenino",
            "accent": "American Blend",
            "category": "⭐ Mezclas Educativas (Blends)",
            "recommended": True,
            "description": "Mezcla estelar recomendada para e-learning: combina la claridad nítida de Bella con el ritmo cálido y pausado de Sarah.",
            "engine": "kokoro"
        },
        {
            "id": "af_heart,af_nicole",
            "name": "Heart & Nicole (Mezcla Didáctica)",
            "gender": "Femenino",
            "accent": "American Blend",
            "category": "⭐ Mezclas Educativas (Blends)",
            "recommended": False,
            "description": "Fusión de calidez empática y articulación metódica para tutoriales paso a paso.",
            "engine": "kokoro"
        },
        {
            "id": "am_adam,am_michael",
            "name": "Adam & Michael (Mezcla Académica)",
            "gender": "Masculino",
            "accent": "American Blend",
            "category": "⭐ Mezclas Educativas (Blends)",
            "recommended": False,
            "description": "Tono documental formal y robusto para conferencias o lecciones científicas.",
            "engine": "kokoro"
        },
        # --- AMERICAN FEMALE (11 VOCES) ---
        {
            "id": "af_heart",
            "name": "Heart (Insignia Kokoro)",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": True,
            "description": "Voz insignia de Kokoro. Calidez humana insuperable y máxima naturalidad para e-learning.",
            "engine": "kokoro"
        },
        {
            "id": "af_bella",
            "name": "Bella",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Articulada, expresiva y didáctica.",
            "engine": "kokoro"
        },
        {
            "id": "af_sarah",
            "name": "Sarah",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Voz juvenil, amigable y entusiasta con ritmo cadencioso.",
            "engine": "kokoro"
        },
        {
            "id": "af_nicole",
            "name": "Nicole",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono paciente y profesional, perfecto para guías instructivas.",
            "engine": "kokoro"
        },
        {
            "id": "af_alloy",
            "name": "Alloy",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono versátil y directo, similar a asistentes modernos.",
            "engine": "kokoro"
        },
        {
            "id": "af_aoede",
            "name": "Aoede",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono suave, fluido y envolvente.",
            "engine": "kokoro"
        },
        {
            "id": "af_jessica",
            "name": "Jessica",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Locución clara y formal para presentaciones de negocios.",
            "engine": "kokoro"
        },
        {
            "id": "af_kore",
            "name": "Kore",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono calmo y seguro para lecturas reflexivas.",
            "engine": "kokoro"
        },
        {
            "id": "af_nova",
            "name": "Nova",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Energética, dinámica y motivacional.",
            "engine": "kokoro"
        },
        {
            "id": "af_river",
            "name": "River",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono moderno con textura acústica natural.",
            "engine": "kokoro"
        },
        {
            "id": "af_sky",
            "name": "Sky",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Voz luminosa y positiva para módulos de bienvenida o síntesis.",
            "engine": "kokoro"
        },
        # --- AMERICAN MALE (9 VOCES) ---
        {
            "id": "am_adam",
            "name": "Adam (Recomendado)",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": True,
            "description": "Narrador clásico estilo documental y conferencias académicas.",
            "engine": "kokoro"
        },
        {
            "id": "am_michael",
            "name": "Michael",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Voz madura y técnica para temas científicos.",
            "engine": "kokoro"
        },
        {
            "id": "am_echo",
            "name": "Echo",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Tono pausado, ideal para meditaciones o lecturas reflexivas.",
            "engine": "kokoro"
        },
        {
            "id": "am_eric",
            "name": "Eric",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Locución amena y conversacional para talleres prácticos.",
            "engine": "kokoro"
        },
        {
            "id": "am_fenrir",
            "name": "Fenrir",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Voz profunda y resonante para narraciones dramáticas.",
            "engine": "kokoro"
        },
        {
            "id": "am_liam",
            "name": "Liam",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Tono joven y dinámico para audiencias jóvenes o universitarias.",
            "engine": "kokoro"
        },
        {
            "id": "am_onyx",
            "name": "Onyx",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Voz grave y autorizada para síntesis conceptuales.",
            "engine": "kokoro"
        },
        {
            "id": "am_puck",
            "name": "Puck",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Voz ágil y espontánea.",
            "engine": "kokoro"
        },
        {
            "id": "am_santa",
            "name": "Santa",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Tono cálido, festivo y característico.",
            "engine": "kokoro"
        },
        # --- BRITISH FEMALE (4 VOCES) ---
        {
            "id": "bf_emma",
            "name": "Emma (Académica UK)",
            "gender": "Femenino",
            "accent": "British",
            "category": "British Female (UK)",
            "recommended": False,
            "description": "Acento británico elegante y pedagógico.",
            "engine": "kokoro"
        },
        {
            "id": "bf_alice",
            "name": "Alice",
            "gender": "Femenino",
            "accent": "British",
            "category": "British Female (UK)",
            "recommended": False,
            "description": "Voz británica articulada y refinada.",
            "engine": "kokoro"
        },
        {
            "id": "bf_isabella",
            "name": "Isabella",
            "gender": "Femenino",
            "accent": "British",
            "category": "British Female (UK)",
            "recommended": False,
            "description": "Voz británica formal y suave.",
            "engine": "kokoro"
        },
        {
            "id": "bf_lily",
            "name": "Lily",
            "gender": "Femenino",
            "accent": "British",
            "category": "British Female (UK)",
            "recommended": False,
            "description": "Tono joven británico, claro y melodioso.",
            "engine": "kokoro"
        },
        # --- BRITISH MALE (4 VOCES) ---
        {
            "id": "bm_george",
            "name": "George (Académico UK)",
            "gender": "Masculino",
            "accent": "British",
            "category": "British Male (UK)",
            "recommended": False,
            "description": "Narrador clásico británico con presencia autorizada.",
            "engine": "kokoro"
        },
        {
            "id": "bm_daniel",
            "name": "Daniel",
            "gender": "Masculino",
            "accent": "British",
            "category": "British Male (UK)",
            "recommended": False,
            "description": "Voz británica sobria y catedrática.",
            "engine": "kokoro"
        },
        {
            "id": "bm_fable",
            "name": "Fable",
            "gender": "Masculino",
            "accent": "British",
            "category": "British Male (UK)",
            "recommended": False,
            "description": "Estilo cuenta-cuentos o narrador literario británico.",
            "engine": "kokoro"
        },
        {
            "id": "bm_lewis",
            "name": "Lewis",
            "gender": "Masculino",
            "accent": "British",
            "category": "British Male (UK)",
            "recommended": False,
            "description": "Voz británica precisa y clara.",
            "engine": "kokoro"
        },
    ]
}

# Kokoro voice IDs quick lookup set
KOKORO_VOICES = {v["id"] for v in VOICES_CATALOG["en"]}

# =========================================================================
#  Motor 1: Microsoft Edge Neural TTS (Español)
# =========================================================================

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

# =========================================================================
#  Motor 2: Kokoro-82M TTS con GPU (Inglés)
# =========================================================================

_kokoro_pipelines: Dict[str, Any] = {}
_kokoro_lock = asyncio.Lock()

def get_kokoro_pipeline(lang_code: str = 'a'):
    """Inicialización bajo demanda (Lazy loading) de Kokoro en GPU o CPU."""
    global _kokoro_pipelines
    if lang_code not in _kokoro_pipelines:
        import torch
        from kokoro import KPipeline
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Inicializando Kokoro KPipeline (lang='{lang_code}', device='{device}')...")
        _kokoro_pipelines[lang_code] = KPipeline(lang_code=lang_code, device=device)
    return _kokoro_pipelines[lang_code]


def generate_kokoro_audio(text: str, voice: str, speed: float = 0.95, audio_format: str = "mp3") -> bytes:
    """
    Genera audio con Kokoro-82M a 24000 Hz. Exporta en MP3 (192kbps) o WAV 16-bit.
    Soporta voces individuales y mezclas separadas por comas (ej. 'af_bella,af_sarah').
    """
    import torch
    import soundfile as sf
    import numpy as np

    # Pre-procesar pausas para guiones
    clean_text = re.sub(r'\[(?:pausa|pause|silence)\]', '... ', text, flags=re.IGNORECASE)

    # Limpiar y normalizar lista de voces para soportar mezclas arbitrarias con o sin espacios
    cleaned_voices = ",".join(v.strip() for v in voice.split(",") if v.strip())
    first_voice = cleaned_voices.split(",")[0] if cleaned_voices else "af_heart"

    # Detectar si la voz es británica ('b') o americana ('a')
    lang_code = 'b' if first_voice.startswith('b') else 'a'
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

    return {
        "status": "connected",
        "gpu_available": cuda_ok,
        "device": device_name,
        "default_format": "mp3",
        "supported_formats": ["mp3", "wav"],
        "engines": {
            "spanish": "Microsoft Edge Neural (Alta velocidad, 0 VRAM)",
            "english": "Kokoro-82M (Acelerado por GPU CUDA)"
        }
    }


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None          # Ej: "es-MX-JorgeNeural" o "af_heart"
    speaker_wav: Optional[str] = None    # Compatibilidad previa ("es-MX-JorgeNeural.wav")
    language: Optional[str] = None       # "es" o "en"
    speed: Optional[float] = 0.95        # 0.95x = Ritmo pedagógico recomendado
    format: Optional[str] = "mp3"        # "mp3" (recomendado, ~10x más ligero) o "wav"
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
    - Si la voz es de Kokoro (o idioma 'en'): Procesa en GPU con Kokoro-82M.
    - Si la voz es de Edge-TTS (o idioma 'es'): Procesa con Microsoft Edge Neural.
    Retorna el stream binario de audio en formato MP3 (por omisión) o WAV.
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

    # Determinar velocidad pedagógica (por omisión 0.95x para lecciones claras)
    speed = req.speed if req.speed is not None else 0.95

    # Determinar formato de salida (mp3 por omisión)
    audio_format = (req.format or "mp3").lower().strip()
    if audio_format not in ["mp3", "wav"]:
        audio_format = "mp3"

    media_type = "audio/mpeg" if audio_format == "mp3" else "audio/wav"

    # 1. Caso Kokoro (Inglés y Mezclas de Voces)
    is_kokoro = (
        voice_id in KOKORO_VOICES
        or lang == "en"
        or voice_id.startswith(("af_", "am_", "bf_", "bm_"))
        or ("," in voice_id and any(v.strip().startswith(("af_", "am_", "bf_", "bm_")) for v in voice_id.split(",")))
    )
    if is_kokoro:
        try:
            print(f"[TTS] Sintetizando en inglés con Kokoro-82M (Voz: {voice_id}, Speed: {speed}, Format: {audio_format})...")
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

    # 2. Caso Edge Neural (Español u otras voces Microsoft)
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
    return {"success": True, "message": "Motores Edge-TTS y Kokoro listos para síntesis."}

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
