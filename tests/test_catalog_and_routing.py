import pytest
from app import VOICES_CATALOG, KOKORO_VOICES, MIMO_VOICES

def test_voices_catalog_structure():
    assert "es" in VOICES_CATALOG
    assert "en" in VOICES_CATALOG
    assert len(VOICES_CATALOG["es"]) > 0
    assert len(VOICES_CATALOG["en"]) > 0

    required_fields = {
        "id", "name", "gender", "accent", "category",
        "recommended", "description", "engine"
    }

    for lang in ["es", "en"]:
        for voice in VOICES_CATALOG[lang]:
            for field in required_fields:
                assert field in voice, f"Voice {voice.get('id')} in '{lang}' missing field '{field}'"
            assert voice["engine"] in {"edge-tts", "kokoro", "mimo"}, (
                f"Invalid engine '{voice['engine']}' for voice {voice['id']}"
            )

def test_recommended_voices_exist():
    rec_es = [v for v in VOICES_CATALOG["es"] if v.get("recommended")]
    rec_en = [v for v in VOICES_CATALOG["en"] if v.get("recommended")]
    assert len(rec_es) >= 1, "Debe existir al menos una voz recomendada en español"
    assert len(rec_en) >= 1, "Debe existir al menos una voz recomendada en inglés"

def test_kokoro_and_mimo_lookup_sets():
    assert len(KOKORO_VOICES) > 0
    assert len(MIMO_VOICES) > 0
    assert "mimo-Chloe" in MIMO_VOICES
    assert "af_heart" in KOKORO_VOICES
    assert "es-MX-JorgeNeural" not in KOKORO_VOICES
    assert "es-MX-JorgeNeural" not in MIMO_VOICES

def test_engine_identification_logic():
    # Helper replicating the identification rules in app.py
    def identify_engine(voice_id: str, lang: str = "es") -> str:
        if not voice_id:
            voice_id = "af_heart" if lang == "en" else "es-MX-JorgeNeural"

        is_mimo = (
            voice_id in MIMO_VOICES
            or voice_id.lower().startswith("mimo-")
            or voice_id.lower().startswith("mimo_")
            or voice_id.lower() in ["chloe", "mia", "milo", "dean", "mimo_default"]
        )
        if is_mimo:
            return "mimo"

        is_kokoro = (
            voice_id in KOKORO_VOICES
            or lang == "en"
            or voice_id.startswith(("af_", "am_", "bf_", "bm_", "ef_", "em_"))
            or ("," in voice_id and any(v.strip().startswith(("af_", "am_", "bf_", "bm_", "ef_", "em_")) for v in voice_id.split(",")))
        )
        if is_kokoro:
            return "kokoro"

        return "edge-tts"

    assert identify_engine("es-MX-JorgeNeural", "es") == "edge-tts"
    assert identify_engine("es-CO-GonzaloNeural", "es") == "edge-tts"
    assert identify_engine("af_heart", "en") == "kokoro"
    assert identify_engine("af_bella,af_sarah", "en") == "kokoro"
    assert identify_engine("ef_dora,af_sarah", "es") == "kokoro"
    assert identify_engine("mimo-Chloe", "en") == "mimo"
    assert identify_engine("mimo-Dean", "en") == "mimo"
    assert identify_engine("", "es") == "edge-tts"
    assert identify_engine("", "en") == "kokoro"

def test_legacy_speaker_filename_resolution():
    sample_wav = "es-MX-JorgeNeural.wav"
    resolved = sample_wav[:-4] if sample_wav.lower().endswith(".wav") else sample_wav
    assert resolved == "es-MX-JorgeNeural"
