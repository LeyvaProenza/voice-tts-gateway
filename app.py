import os
import sys
import signal
import subprocess
import io
import re
import edge_tts
from pydub import AudioSegment
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI(
    title="Voice-TTS Gateway",
    description="API Gateway para clonacion de voz con XTTS. Antigravity envia texto y recibe WAV.",
    version="2.0.0",
)

# Enable CORS for all origins (Antigravity needs to call this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
TTS_SERVER_URL = "http://127.0.0.1:8020"
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SPEAKERS_DIR = os.path.join(WORKSPACE_DIR, "speakers")
MODELS_DIR = os.path.join(WORKSPACE_DIR, "models")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "output")

# Ensure required directories exist
os.makedirs(SPEAKERS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Track the XTTS server subprocess
_xtts_process = None


# =========================================================================
#  XTTS Server Management
# =========================================================================

@app.get("/api/status")
def get_status():
    """Check if the local XTTS API Server is running and responding."""
    global _xtts_process
    try:
        response = requests.get(f"{TTS_SERVER_URL}/docs", timeout=2)
        if response.status_code == 200:
            return {"status": "connected", "url": TTS_SERVER_URL}
    except requests.exceptions.RequestException:
        pass
    # If our managed process died, clean up reference
    if _xtts_process and _xtts_process.poll() is not None:
        _xtts_process = None
    return {"status": "disconnected", "url": TTS_SERVER_URL}


@app.post("/api/server/start")
def start_server():
    """Start the local XTTS API server as a background subprocess."""
    global _xtts_process

    # Check if already running
    try:
        response = requests.get(f"{TTS_SERVER_URL}/docs", timeout=2)
        if response.status_code == 200:
            return {"success": True, "message": "El servidor ya esta activo."}
    except requests.exceptions.RequestException:
        pass

    # Build command
    python_exe = os.path.join(WORKSPACE_DIR, ".venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        return {"success": False, "error": "No se encontro el entorno virtual .venv"}

    cmd = [
        python_exe, "-m", "xtts_api_server",
        "--port", "8020",
        "--host", "127.0.0.1",
        "--speaker-folder", SPEAKERS_DIR,
        "--model-folder", MODELS_DIR,
        "--lowvram",
    ]

    log_path = os.path.join(WORKSPACE_DIR, "tts_server.log")
    try:
        log_file = open(log_path, "w", encoding="utf-8")
        _xtts_process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return {
            "success": True,
            "message": "Servidor XTTS iniciando... Puede tardar 20-60 segundos en cargar el modelo.",
            "pid": _xtts_process.pid,
            "log": log_path,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/server/stop")
def stop_server():
    """Stop the local XTTS API server."""
    global _xtts_process

    killed = False

    # Try killing our managed subprocess first
    if _xtts_process and _xtts_process.poll() is None:
        try:
            _xtts_process.terminate()
            _xtts_process.wait(timeout=5)
            killed = True
        except Exception:
            try:
                _xtts_process.kill()
                killed = True
            except Exception:
                pass
        _xtts_process = None

    # Also try finding by port (in case it was started externally via .bat)
    if not killed and sys.platform == "win32":
        try:
            result = subprocess.run(
                'netstat -aon | findstr :8020 | findstr LISTENING',
                capture_output=True, text=True, shell=True
            )
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                    killed = True
        except Exception:
            pass

    if killed:
        return {"success": True, "message": "Servidor XTTS detenido."}
    else:
        return {"success": True, "message": "No se encontro ningun servidor activo."}


@app.get("/api/server/log")
def get_server_log(lines: int = Query(50, description="Number of tail lines to return")):
    """Return the last N lines of the XTTS server log."""
    log_path = os.path.join(WORKSPACE_DIR, "tts_server.log")
    if not os.path.exists(log_path):
        return {"log": "", "exists": False}
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return {"log": "".join(tail), "exists": True}
    except Exception as e:
        return {"log": f"Error reading log: {e}", "exists": True}


# =========================================================================
#  Speaker / Voice Management
# =========================================================================

@app.get("/api/speakers")
def get_speakers():
    """List all available reference voices (.wav) in the speakers directory."""
    try:
        files = os.listdir(SPEAKERS_DIR)
        wav_files = sorted([f for f in files if f.lower().endswith(".wav")])
        speaker_info = []
        for f in wav_files:
            fpath = os.path.join(SPEAKERS_DIR, f)
            size_kb = round(os.path.getsize(fpath) / 1024, 1)
            speaker_info.append({"name": f, "size_kb": size_kb})
        return {"speakers": speaker_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/speakers/upload")
async def upload_speaker(file: UploadFile = File(...)):
    """Upload a new .wav reference voice to the speakers directory."""
    if not file.filename.lower().endswith(".wav"):
        return {"success": False, "error": "Solo se aceptan archivos .wav"}

    file_path = os.path.join(SPEAKERS_DIR, file.filename)
    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        size_kb = round(len(content) / 1024, 1)
        return {"success": True, "filename": file.filename, "size_kb": size_kb}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/speakers/{filename}")
def delete_speaker(filename: str):
    """Delete a reference voice file."""
    file_path = os.path.join(SPEAKERS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    try:
        os.remove(file_path)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/speakers/{filename}/audio")
def get_speaker_audio(filename: str):
    """Stream a speaker reference wav for preview playback."""
    file_path = os.path.join(SPEAKERS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path, media_type="audio/wav")


# =========================================================================
#  TTS API  -  This is what Antigravity calls
# =========================================================================

EDGE_VOICES_MAP = {
    "es-MX-DaliaNeural.wav": "es-MX-DaliaNeural",
    "es-MX-JorgeNeural.wav": "es-MX-JorgeNeural",
    "es-ES-AlvaroNeural.wav": "es-ES-AlvaroNeural",
    "es-ES-ElviraNeural.wav": "es-ES-ElviraNeural",
    "es-US-AlonsoNeural.wav": "es-US-AlonsoNeural",
    "es-US-PalomaNeural.wav": "es-US-PalomaNeural",
    "es-AR-ElenaNeural.wav": "es-AR-ElenaNeural",
    "es-AR-TomasNeural.wav": "es-AR-TomasNeural",
    "es-CO-GonzaloNeural.wav": "es-CO-GonzaloNeural",
    "es-CO-SalomeNeural.wav": "es-CO-SalomeNeural",
}

async def generate_direct_edge_tts(text: str, voice_name: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice_name)
    mp3_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_data += chunk["data"]
            
    # Convert MP3 bytes to WAV bytes using pydub
    audio = AudioSegment.from_file(io.BytesIO(mp3_data), format="mp3")
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    return wav_io.getvalue()

def convert_to_seseo(text: str) -> str:
    """
    Replaces Spanish ceceo (Castilian lisp) spellings with seseo (Latin American)
    so the XTTS European Spanish model pronounces them with 's' instead of 'th'.
    """
    # Replace 'z' and 'Z' with 's' and 'S'
    text = re.sub(r'z', 's', text)
    text = re.sub(r'Z', 'S', text)
    # Replace 'c' followed by 'e', 'i', 'é', 'í' with 's'
    text = re.sub(r'c([eiéí])', r's\1', text)
    text = re.sub(r'C([eiéí])', r'S\1', text)
    return text

class TTSRequest(BaseModel):
    text: str
    speaker_wav: str
    language: str = "es"
    temperature: Optional[float] = None
    length_penalty: Optional[float] = None
    repetition_penalty: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    remove_ceceo: Optional[bool] = True

@app.post("/api/tts")
async def tts_generate(req: TTSRequest):
    """
    Main TTS endpoint for Antigravity.

    Receives text + speaker_wav name + language + optional parameters.
    Returns the generated WAV audio bytes directly (Content-Type: audio/wav).

    Example call from Antigravity:
        POST http://localhost:8000/api/tts
        Content-Type: application/json
        {
          "text": "Hola mundo", 
          "speaker_wav": "mi_voz.wav", 
          "language": "es",
          "temperature": 0.75,
          "length_penalty": 1.0,
          "repetition_penalty": 5.0,
          "top_k": 50,
          "top_p": 0.85,
          "remove_ceceo": true
        }

    Response: binary WAV audio (save directly as .wav file)
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="El campo 'text' no puede estar vacio.")
    if not req.speaker_wav.strip():
        raise HTTPException(status_code=400, detail="El campo 'speaker_wav' es requerido.")

    # Bypass XTTS and generate directly with edge-tts if it's a Microsoft Neural voice
    speaker_clean = req.speaker_wav.strip()
    voice_id = speaker_clean[:-4] if speaker_clean.lower().endswith(".wav") else speaker_clean
    if "Neural" in voice_id:
        try:
            print(f"Bypass: Generando audio directo con Edge-TTS para {voice_id} (Calidad de estudio)")
            wav_bytes = await generate_direct_edge_tts(req.text, voice_id)
            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={"Content-Disposition": "attachment; filename=tts_output.wav"},
            )
        except Exception as e:
            print(f"Error generando directo de Edge-TTS para {voice_id}: {e}. Usando fallback a XTTS local...")

    # For XTTS local cloning, apply seseo to remove Castilian lisp if requested
    text_to_send = req.text
    if req.remove_ceceo if req.remove_ceceo is not None else True:
        text_to_send = convert_to_seseo(text_to_send)
        print(f"Seseo aplicado: '{req.text}' -> '{text_to_send}'")

    # Configure generation parameters on the XTTS server
    settings = {
        "temperature": req.temperature if req.temperature is not None else 0.75,
        "length_penalty": req.length_penalty if req.length_penalty is not None else 1.0,
        "repetition_penalty": req.repetition_penalty if req.repetition_penalty is not None else 5.0,
        "top_k": req.top_k if req.top_k is not None else 50,
        "top_p": req.top_p if req.top_p is not None else 0.85,
        "speed": 1.0,
        "enable_text_splitting": True,
        "stream_chunk_size": 100
    }

    try:
        requests.post(f"{TTS_SERVER_URL}/set_tts_settings", json=settings, timeout=5)
    except Exception as e:
        print(f"Advertencia: No se pudieron aplicar los ajustes en el servidor XTTS: {e}")

    payload = {
        "text": text_to_send,
        "speaker_wav": req.speaker_wav,
        "language": req.language,
    }

    try:
        response = requests.post(
            f"{TTS_SERVER_URL}/tts_to_audio/",
            json=payload,
            timeout=180,
        )

        if response.status_code != 200:
            try:
                err = response.json().get("detail", response.text)
            except Exception:
                err = response.text
            raise HTTPException(
                status_code=502,
                detail=f"XTTS server error ({response.status_code}): {err}"
            )

        return Response(
            content=response.content,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=tts_output.wav"},
        )

    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="El servidor XTTS no esta activo. Inicia el servidor primero.")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="El servidor XTTS tardo demasiado en responder.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
#  Favicon Handler (prevents 404 logs)
# =========================================================================
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


# =========================================================================
#  Static Files (Frontend UI)
# =========================================================================
app.mount("/", StaticFiles(directory=os.path.join(WORKSPACE_DIR, "static"), html=True), name="static")

