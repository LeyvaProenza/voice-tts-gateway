import io
import json
import base64
import urllib.error
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pydub import AudioSegment
import numpy as np

from app import (
    generate_edge_tts_audio,
    generate_kokoro_audio,
    generate_mimo_audio,
    synthesize_text_segment,
    generate_synced_subtitle_audio,
    generate_continuous_subtitle_audio,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def create_dummy_wav_bytes(duration_ms=500, frame_rate=24000):
    seg = AudioSegment.silent(duration=duration_ms, frame_rate=frame_rate)
    buf = io.BytesIO()
    seg.export(buf, format="wav")
    return buf.getvalue()

# ---------------------------------------------------------------------------
# 1. Edge-TTS Unit Tests (Mocked)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_generate_edge_tts_audio_mp3_success():
    fake_mp3 = b"FAKE_MP3_STREAM_DATA"

    async def fake_stream():
        yield {"type": "audio", "data": fake_mp3}

    with patch("edge_tts.Communicate") as mock_comm:
        instance = MagicMock()
        instance.stream = fake_stream
        mock_comm.return_value = instance

        result = await generate_edge_tts_audio(
            text="Texto con [pausa] intermedia",
            voice_name="es-MX-JorgeNeural",
            speed=0.95,
            audio_format="mp3"
        )

        assert result == fake_mp3
        # Verificar que se calculó el rate (-5%)
        mock_comm.assert_called_once_with("Texto con ...  intermedia", "es-MX-JorgeNeural", rate="-5%")

@pytest.mark.asyncio
async def test_generate_edge_tts_audio_empty_raises():
    async def empty_stream():
        if False:
            yield None

    with patch("edge_tts.Communicate") as mock_comm:
        instance = MagicMock()
        instance.stream = empty_stream
        mock_comm.return_value = instance

        with pytest.raises(ValueError, match="Edge-TTS no devolvió datos de audio"):
            await generate_edge_tts_audio("Prueba", "es-MX-JorgeNeural")

# ---------------------------------------------------------------------------
# 2. Kokoro Unit Tests (Mocked)
# ---------------------------------------------------------------------------
def test_generate_kokoro_audio_success():
    # Simular pipeline que devuelve un chunk de audio numpy
    sample_rate = 24000
    dummy_audio = np.zeros(sample_rate, dtype=np.float32)

    mock_pipeline = MagicMock()
    mock_pipeline.return_value = [("graphemes", "phonemes", dummy_audio)]

    with patch("engines.kokoro_engine.get_kokoro_pipeline", return_value=mock_pipeline) as mock_get_pipeline:
        wav_out = generate_kokoro_audio("Hello [pause] world", "af_heart", speed=1.0, audio_format="wav")
        assert len(wav_out) > 0
        assert wav_out.startswith(b"RIFF")
        mock_get_pipeline.assert_called_once_with("a")

    with patch("engines.kokoro_engine.get_kokoro_pipeline", return_value=mock_pipeline) as mock_get_pipeline:
        # Voz en español de Kokoro
        _ = generate_kokoro_audio("Hola mundo", "ef_dora", speed=0.95, audio_format="mp3")
        mock_get_pipeline.assert_called_once_with("e")

def test_generate_kokoro_audio_empty_raises():
    mock_pipeline = MagicMock()
    mock_pipeline.return_value = []

    with patch("engines.kokoro_engine.get_kokoro_pipeline", return_value=mock_pipeline):
        with pytest.raises(ValueError, match="Kokoro no devolvió datos de audio"):
            generate_kokoro_audio("Hello", "af_heart")

# ---------------------------------------------------------------------------
# 3. Xiaomi MiMo Unit Tests (Mocked)
# ---------------------------------------------------------------------------
def test_generate_mimo_audio_missing_api_key():
    with patch("engines.mimo_engine.get_mimo_api_key", return_value=None):
        with pytest.raises(ValueError, match="MIMO_API_KEY"):
            generate_mimo_audio("Test", "mimo-Chloe")

def test_generate_mimo_audio_success_mocked():
    raw_wav = create_dummy_wav_bytes(duration_ms=300)
    b64_audio = base64.b64encode(raw_wav).decode("utf-8")
    fake_response_dict = {
        "choices": [
            {
                "message": {
                    "audio": {
                        "data": b64_audio
                    }
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(fake_response_dict).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("engines.mimo_engine.get_mimo_api_key", return_value="dummy_test_key_123"):
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
            result = generate_mimo_audio(
                text="Welcome to class",
                voice_name="mimo-Chloe",
                speed=0.95,
                audio_format="wav",
                style_prompt="Energetic and cheerful"
            )

            assert len(result) > 0
            assert result.startswith(b"RIFF")
            # Verificar llamada a urlopen
            req_arg = mock_urlopen.call_args[0][0]
            assert req_arg.full_url == "https://api.xiaomimimo.com/v1/chat/completions"
            assert req_arg.headers["Authorization"] == "Bearer dummy_test_key_123"
            sent_data = json.loads(req_arg.data.decode("utf-8"))
            assert sent_data["model"] == "mimo-v2.5-tts"
            assert sent_data["audio"]["voice"] == "Chloe"
            # Verificar que el prompt incluye la instrucción y el matiz de velocidad pedagógica
            user_msg = next(m["content"] for m in sent_data["messages"] if m["role"] == "user")
            assert "Energetic and cheerful" in user_msg

def test_generate_mimo_audio_http_error_handled():
    mock_http_error = urllib.error.HTTPError(
        url="https://api.xiaomimimo.com",
        code=401,
        msg="Unauthorized",
        hdrs={},
        fp=io.BytesIO(b'{"error": "Invalid API Key"}')
    )

    with patch("engines.mimo_engine.get_mimo_api_key", return_value="bad_key"):
        with patch("urllib.request.urlopen", side_effect=mock_http_error):
            with pytest.raises(RuntimeError, match="Error HTTP en Xiaomi MiMo API"):
                generate_mimo_audio("Test", "mimo-Chloe")

# ---------------------------------------------------------------------------
# 4. Engine Dispatcher (synthesize_text_segment)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_synthesize_text_segment_dispatching():
    dummy_wav = create_dummy_wav_bytes(200)

    # Caso MiMo
    with patch("subtitles.generate_mimo_audio", return_value=dummy_wav) as mock_mimo:
        seg = await synthesize_text_segment("Hi", "mimo-Chloe")
        assert isinstance(seg, AudioSegment)
        assert mock_mimo.called

    # Caso Kokoro
    with patch("subtitles.generate_kokoro_audio", return_value=dummy_wav) as mock_kokoro:
        seg = await synthesize_text_segment("Hello", "af_heart")
        assert isinstance(seg, AudioSegment)
        assert mock_kokoro.called

    # Caso Edge-TTS
    with patch("subtitles.generate_edge_tts_audio", new_callable=AsyncMock) as mock_edge:
        mock_edge.return_value = dummy_wav
        seg = await synthesize_text_segment("Hola", "es-MX-JorgeNeural")
        assert isinstance(seg, AudioSegment)
        assert mock_edge.called

# ---------------------------------------------------------------------------
# 5. Subtitle Audio Generation Tests (Mocked)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_generate_synced_subtitle_audio_mocked():
    subtitles = [
        {"index": 1, "start_ms": 500, "end_ms": 1500, "duration_ms": 1000, "text": "Segmento 1"},
        {"index": 2, "start_ms": 2500, "end_ms": 3500, "duration_ms": 1000, "text": "Segmento 2"},
    ]

    dummy_seg = AudioSegment.silent(duration=800)

    with patch("subtitles.synthesize_text_segment", new_callable=AsyncMock) as mock_synth:
        mock_synth.return_value = dummy_seg
        audio_mp3 = await generate_synced_subtitle_audio(subtitles, "es-MX-JorgeNeural", audio_format="mp3")
        assert len(audio_mp3) > 0
        assert mock_synth.call_count == 2

@pytest.mark.asyncio
async def test_generate_continuous_subtitle_audio_mocked():
    subtitles = [
        {"index": 1, "start_ms": 0, "end_ms": 1000, "duration_ms": 1000, "text": "Primera oración."},
        {"index": 2, "start_ms": 1500, "end_ms": 2500, "duration_ms": 1000, "text": "Segunda oración."},
    ]

    fake_bytes = b"CONTINUOUS_AUDIO_BYTES"

    with patch("subtitles.generate_edge_tts_audio", new_callable=AsyncMock) as mock_edge:
        mock_edge.return_value = fake_bytes
        result = await generate_continuous_subtitle_audio(subtitles, "es-MX-JorgeNeural", audio_format="mp3")
        assert result == fake_bytes
        # Verificar que unió con puntos suspensivos
        mock_edge.assert_called_once_with(
            "Primera oración. ... Segunda oración.",
            "es-MX-JorgeNeural",
            0.95,
            "mp3"
        )
