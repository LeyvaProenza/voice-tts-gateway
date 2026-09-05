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
            "recommended": True,
            "description": "Tono sereno, cálido y explicativo. Dicción impecable para docencia y tutoriales.",
            "engine": "edge-tts"
        },
        {
            "id": "es-MX-DaliaNeural",
            "name": "Dalia (Recomendada)",
            "gender": "Femenino",
            "accent": "México",
            "recommended": True,
            "description": "Voz clara, empática y natural, excelente para exposiciones y material formativo.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CO-GonzaloNeural",
            "name": "Gonzalo",
            "gender": "Masculino",
            "accent": "Colombia",
            "recommended": False,
            "description": "Acento neutro y formal, ideal para lecturas académicas o científicas.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CO-SalomeNeural",
            "name": "Salomé",
            "gender": "Femenino",
            "accent": "Colombia",
            "recommended": False,
            "description": "Tono pausado y suave, muy adecuado para audiolibros educativos.",
            "engine": "edge-tts"
        },
        {
            "id": "es-AR-TomasNeural",
            "name": "Tomás",
            "gender": "Masculino",
            "accent": "Argentina",
            "recommended": False,
            "description": "Locución segura y profesional.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CL-CatalinaNeural",
            "name": "Catalina",
            "gender": "Femenino",
            "accent": "Chile",
            "recommended": False,
            "description": "Voz limpia, expresiva y didáctica.",
            "engine": "edge-tts"
        },
        {
            "id": "es-US-AlonsoNeural",
            "name": "Alonso",
            "gender": "Masculino",
            "accent": "Latino Neutro (EE.UU.)",
            "recommended": False,
            "description": "Locución dinámica y articulada para presentaciones corporativas.",
            "engine": "edge-tts"
        },
        {
            "id": "es-US-PalomaNeural",
            "name": "Paloma",
            "gender": "Femenino",
            "accent": "Latino Neutro (EE.UU.)",
            "recommended": False,
            "description": "Tono joven, fresco y claro.",
            "engine": "edge-tts"
        },
        {
            "id": "es-ES-AlvaroNeural",
            "name": "Álvaro",
            "gender": "Masculino",
            "accent": "España",
            "recommended": False,
            "description": "Acento castellano formal y bien articulado.",
            "engine": "edge-tts"
        },
        {
            "id": "es-ES-ElviraNeural",
            "name": "Elvira",
            "gender": "Femenino",
            "accent": "España",
            "recommended": False,
            "description": "Acento castellano clásico y sereno.",
            "engine": "edge-tts"
        },
    ],
    "en": [
        {
            "id": "af_heart",
            "name": "Heart (Recomendada)",
            "gender": "Femenino",
            "accent": "American",
            "recommended": True,
            "description": "Voz insignia de Kokoro. Calidez humana insuperable para e-learning.",
            "engine": "kokoro"
        },
        {
            "id": "am_adam",
            "name": "Adam (Recomendado)",
            "gender": "Masculino",
            "accent": "American",
            "recommended": True,
            "description": "Narrador clásico estilo documental y conferencias académicas.",
            "engine": "kokoro"
        },
        {
            "id": "af_bella",
            "name": "Bella",
            "gender": "Femenino",
            "accent": "American",
            "recommended": False,
            "description": "Articulada, expresiva y didáctica.",
            "engine": "kokoro"
        },
        {
            "id": "af_nicole",
            "name": "Nicole",
            "gender": "Femenino",
            "accent": "American",
            "recommended": False,
            "description": "Tono paciente y profesional, perfecto para guías paso a paso.",
            "engine": "kokoro"
        },
        {
            "id": "af_sarah",
            "name": "Sarah",
            "gender": "Femenino",
            "accent": "American",
            "recommended": False,
            "description": "Voz juvenil, amigable y entusiasta.",
            "engine": "kokoro"
        },
        {
            "id": "am_michael",
            "name": "Michael",
            "gender": "Masculino",
            "accent": "American",
            "recommended": False,
            "description": "Voz madura y técnica para temas científicos.",
            "engine": "kokoro"
        },
        {
            "id": "am_echo",
            "name": "Echo",
            "gender": "Masculino",
            "accent": "American",
            "recommended": False,
            "description": "Tono pausado, ideal para meditaciones o lecturas reflexivas.",
            "engine": "kokoro"
        },
        {
            "id": "bf_emma",
            "name": "Emma (Académica UK)",
            "gender": "Femenino",
            "accent": "British",
            "recommended": False,
            "description": "Acento británico elegante y pedagógico.",
            "engine": "kokoro"
        },
        {
            "id": "bf_isabella",
            "name": "Isabella",
            "gender": "Femenino",
            "accent": "British",
            "recommended": False,
            "description": "Voz británica formal y suave.",
            "engine": "kokoro"
        },
        {
            "id": "bm_george",
            "name": "George",
            "gender": "Masculino",
            "accent": "British",
            "recommended": False,
            "description": "Narrador clásico británico con presencia autorizada.",
            "engine": "kokoro"
        },
        {
            "id": "bm_lewis",
            "name": "Lewis",
            "gender": "Masculino",
            "accent": "British",
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

async def generate_edge_tts_audio(text: str, voice_name: str, speed: float = 0.95) -> bytes:
    """
    Genera audio con Edge-TTS y ajusta la tasa de habla para cadencia educativa.
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

    # Convertir MP3 bytes a WAV en memoria
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


def generate_kokoro_audio(text: str, voice: str, speed: float = 0.95) -> bytes:
    """
    Genera audio con Kokoro-82M a 24000 Hz en formato WAV de 16-bit.
    """
    import torch
    import soundfile as sf

    # Pre-procesar pausas para guiones
    clean_text = re.sub(r'\[(?:pausa|pause|silence)\]', '... ', text, flags=re.IGNORECASE)

    # Detectar si la voz es británica ('b') o americana ('a')
    lang_code = 'b' if voice.startswith('b') else 'a'
    pipeline = get_kokoro_pipeline(lang_code)

    generator = pipeline(clean_text, voice=voice, speed=speed, split_pattern=r'\n+')
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
    Retorna el stream binario de audio en formato audio/wav.
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

    # 1. Caso Kokoro (Inglés)
    if voice_id in KOKORO_VOICES or lang == "en" or voice_id.startswith(("af_", "am_", "bf_", "bm_")):
        try:
            print(f"[TTS] Sintetizando en inglés con Kokoro-82M (Voz: {voice_id}, Speed: {speed})...")
            async with _kokoro_lock:
                wav_bytes = await asyncio.to_thread(generate_kokoro_audio, req.text, voice_id, speed)
            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={"Content-Disposition": f"attachment; filename={voice_id}_output.wav"},
            )
        except Exception as e:
            print(f"[TTS Error Kokoro]: {e}")
            raise HTTPException(status_code=500, detail=f"Error en motor Kokoro: {str(e)}")

    # 2. Caso Edge Neural (Español u otras voces Microsoft)
    try:
        print(f"[TTS] Sintetizando con Edge Neural (Voz: {voice_id}, Speed: {speed})...")
        wav_bytes = await generate_edge_tts_audio(req.text, voice_id, speed)
        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={voice_id}_output.wav"},
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
