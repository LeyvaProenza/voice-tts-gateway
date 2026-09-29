"""
Motor Xiaomi MiMo Speech Synthesis v2.5 (Cloud API).
Soporta Modo Director por lenguaje natural y Audio Tags inline ([laughter], [sigh], etc.).
"""

import os
import io
import json
import base64
import urllib.request
import urllib.error
from typing import Optional
from pydub import AudioSegment
from pydub.effects import speedup

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_mimo_api_key() -> Optional[str]:
    """Obtiene la clave de API de MiMo desde el entorno o archivo .env."""
    key = os.environ.get("MIMO_API_KEY")
    if not key:
        env_file = os.path.join(WORKSPACE_DIR, ".env")
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("MIMO_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        os.environ["MIMO_API_KEY"] = key
                        break
    return key


def generate_mimo_audio(
    text: str,
    voice_name: str,
    speed: float = 0.95,
    audio_format: str = "mp3",
    style_prompt: Optional[str] = None
) -> bytes:
    """
    Genera audio usando la API de Xiaomi MiMo Speech Synthesis v2.5.
    Soporta Modo Director (style_prompt) y Audio Tags ([laughter], [sigh], etc.).
    Devuelve audio en formato MP3 (192 kbps) o WAV PCM 16-bit.
    """
    api_key = get_mimo_api_key()
    if not api_key:
        raise ValueError("No se encontró MIMO_API_KEY configurada en el archivo .env ni en las variables de entorno.")

    # Normalizar nombre de la voz: remover prefijo 'mimo-' si existe
    clean_voice = voice_name
    if clean_voice.lower().startswith("mimo-"):
        clean_voice = clean_voice[5:]
    elif clean_voice.lower().startswith("mimo_"):
        clean_voice = clean_voice[5:]

    if not clean_voice:
        clean_voice = "Chloe"

    url = "https://api.xiaomimimo.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Construir mensajes:
    # role: assistant -> Texto a sintetizar (puede incluir tags [laughter], [sigh], etc.)
    # role: user -> Instrucciones de emoción/estilo para el Modo Director
    messages = []
    pace_hint = ""
    if speed is not None:
        if speed <= 0.85:
            pace_hint = " Speak at a slow, clear and methodical educational pace."
        elif speed >= 1.15:
            pace_hint = " Speak at a quick, brisk and dynamic pace."
        elif abs(speed - 0.95) < 0.02:
            pace_hint = " Speak at a calm, clear instructional pace."

    if style_prompt and style_prompt.strip():
        messages.append({"role": "user", "content": style_prompt.strip() + pace_hint})
    else:
        messages.append({"role": "user", "content": "Clear, natural and fluent speech." + pace_hint})

    messages.append({"role": "assistant", "content": text})

    payload = {
        "model": "mimo-v2.5-tts",
        "messages": messages,
        "audio": {
            "format": "wav",
            "voice": clean_voice
        }
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            resp_body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        err_msg = err.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Error HTTP en Xiaomi MiMo API ({err.code}): {err_msg}")
    except Exception as exc:
        raise RuntimeError(f"Fallo al conectar con Xiaomi MiMo API: {str(exc)}")

    choices = resp_body.get("choices", [])
    if not choices:
        raise RuntimeError(f"Xiaomi MiMo no retornó elecciones de audio: {resp_body}")

    audio_b64 = choices[0].get("message", {}).get("audio", {}).get("data")
    if not audio_b64:
        raise RuntimeError(f"Xiaomi MiMo no devolvió datos de audio en la respuesta: {resp_body}")

    wav_bytes = base64.b64decode(audio_b64)
    audio_seg = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
    if speed and speed > 1.05 and speed <= 2.0:
        try:
            audio_seg = speedup(audio_seg, playback_speed=speed)
        except Exception:
            pass

    # Si se solicita MP3, convertir a MP3 a 192 kbps
    if audio_format.lower() == "mp3":
        mp3_io = io.BytesIO()
        audio_seg.export(mp3_io, format="mp3", bitrate="192k")
        return mp3_io.getvalue()

    wav_io = io.BytesIO()
    audio_seg.export(wav_io, format="wav")
    return wav_io.getvalue()
