import io
import pytest
from fastapi.testclient import TestClient
from app import app, MAX_SUBTITLE_FILE_SIZE

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_api_status(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert "gpu_available" in data
    assert "device" in data
    assert data["default_format"] == "mp3"
    assert "mp3" in data["supported_formats"]
    assert "wav" in data["supported_formats"]
    assert "engines" in data
    assert "spanish" in data["engines"]
    assert "english" in data["engines"]
    assert "mimo" in data["engines"]

def test_api_voices(client):
    response = client.get("/api/voices")
    assert response.status_code == 200
    data = response.json()
    assert "es" in data
    assert "en" in data
    assert len(data["es"]) > 0
    assert len(data["en"]) > 0

def test_api_speakers_legacy(client):
    response = client.get("/api/speakers")
    assert response.status_code == 200
    data = response.json()
    assert "speakers" in data
    assert len(data["speakers"]) > 0
    first = data["speakers"][0]
    assert "name" in first
    assert "size_kb" in first

def test_api_server_legacy_endpoints(client):
    r_start = client.post("/api/server/start")
    assert r_start.status_code == 200
    assert r_start.json()["success"] is True

    r_stop = client.post("/api/server/stop")
    assert r_stop.status_code == 200
    assert r_stop.json()["success"] is True

    r_log = client.get("/api/server/log")
    assert r_log.status_code == 200
    assert r_log.json()["exists"] is True

def test_favicon(client):
    response = client.get("/favicon.ico")
    assert response.status_code == 204

def test_api_tts_validation_empty_text(client):
    response = client.post("/api/tts", json={"text": ""})
    assert response.status_code == 400
    assert "vacío" in response.json()["detail"].lower()

    response_whitespace = client.post("/api/tts", json={"text": "   \n\t  "})
    assert response_whitespace.status_code == 400

def test_api_tts_validation_speed_out_of_bounds(client):
    response_low = client.post("/api/tts", json={"text": "Texto válido", "speed": 0.1})
    assert response_low.status_code == 422

    response_high = client.post("/api/tts", json={"text": "Texto válido", "speed": 5.0})
    assert response_high.status_code == 422

def test_api_tts_subtitle_validation(client):
    # Texto vacío
    r_empty = client.post("/api/tts/subtitle", json={"subtitle_text": ""})
    assert r_empty.status_code == 400

    # Texto sin formato de subtítulos
    r_invalid = client.post("/api/tts/subtitle", json={"subtitle_text": "Texto plano sin timestamps"})
    assert r_invalid.status_code == 400

    # Velocidad fuera de rango
    r_speed = client.post("/api/tts/subtitle", json={
        "subtitle_text": "1\n00:00:01,000 --> 00:00:03,000\nHola",
        "speed": 0.05
    })
    assert r_speed.status_code == 422

    # Factor de aceleración fuera de rango
    r_max_speed = client.post("/api/tts/subtitle", json={
        "subtitle_text": "1\n00:00:01,000 --> 00:00:03,000\nHola",
        "max_speed_factor": 0.5
    })
    assert r_max_speed.status_code == 422

def test_api_tts_subtitle_file_too_large(client):
    # Crear payload simulado mayor al límite
    large_payload = b"0" * (MAX_SUBTITLE_FILE_SIZE + 1024)
    files = {"file": ("large_subtitles.srt", io.BytesIO(large_payload), "text/plain")}
    response = client.post("/api/tts/subtitle/file", files=files)
    assert response.status_code == 413
    assert "excede el tamaño máximo" in response.json()["detail"].lower() or "supera el límite" in response.json()["detail"].lower()
