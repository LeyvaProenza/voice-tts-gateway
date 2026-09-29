import pytest
from fastapi.testclient import TestClient
from app import app, generate_edge_tts_audio, generate_kokoro_audio, generate_mimo_audio, get_mimo_api_key

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.mark.asyncio
async def test_live_edge_tts_spanish():
    text = "Hola, esta es una verificación de síntesis en español."
    voice = "es-MX-JorgeNeural"
    audio = await generate_edge_tts_audio(text, voice_name=voice, speed=0.95, audio_format="mp3")
    assert len(audio) > 1000, "El audio generado debe contener datos binarios de MP3"
    assert audio[:3] == b"ID3" or audio[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"), "Debe tener cabecera válida de MP3"

def test_live_kokoro_english_gpu():
    text = "Hello, this is an automated live smoke test for Kokoro AI."
    voice = "af_heart"
    audio = generate_kokoro_audio(text, voice=voice, speed=0.95, audio_format="mp3")
    assert len(audio) > 1000, "El audio de Kokoro debe contener datos binarios de MP3"
    assert audio[:3] == b"ID3" or audio[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")

def test_live_subtitle_api_endpoint(client):
    srt_payload = """1
00:00:00,500 --> 00:00:02,000
Prueba rápida de sincronización.

2
00:00:02,500 --> 00:00:04,000
Segunda frase de prueba.
"""
    response = client.post("/api/tts/subtitle", json={
        "subtitle_text": srt_payload,
        "voice": "es-MX-JorgeNeural",
        "speed": 1.0,
        "mode": "synced",
        "format": "mp3"
    })
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "audio/mpeg"
    assert response.headers.get("X-Subtitle-Count") == "2"
    assert len(response.content) > 5000

def test_live_mimo_cloud_if_key_available():
    api_key = get_mimo_api_key()
    if not api_key:
        pytest.skip("MIMO_API_KEY no encontrada en .env")

    try:
        audio = generate_mimo_audio(
            text="Testing MiMo cloud voice.",
            voice_name="mimo-Chloe",
            speed=0.95,
            audio_format="mp3",
            style_prompt="Clear and natural"
        )
        assert len(audio) > 1000
        assert audio[:3] == b"ID3" or audio[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")
    except Exception as exc:
        pytest.skip(f"Xiaomi MiMo Cloud no disponible temporalmente: {exc}")
