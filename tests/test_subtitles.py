import pytest
from app import parse_subtitles

def test_parse_subtitles_srt_standard():
    srt_content = """1
00:00:01,000 --> 00:00:03,500
Primera línea de prueba.

2
00:00:04,200 --> 00:00:06,800
Segunda línea con
salto de texto.
"""
    result = parse_subtitles(srt_content)
    assert len(result) == 2
    assert result[0]["index"] == 1
    assert result[0]["start_ms"] == 1000
    assert result[0]["end_ms"] == 3500
    assert result[0]["duration_ms"] == 2500
    assert result[0]["text"] == "Primera línea de prueba."

    assert result[1]["index"] == 2
    assert result[1]["start_ms"] == 4200
    assert result[1]["end_ms"] == 6800
    assert result[1]["duration_ms"] == 2600
    assert result[1]["text"] == "Segunda línea con salto de texto."

def test_parse_subtitles_vtt_with_header_and_cue_settings():
    vtt_content = """WEBVTT

cue-intro
00:00:01.500 --> 00:00:04.000 align:center size:50%
Texto con identificador y estilo VTT.

00:00:05.000 --> 00:00:07.500
Segundo bloque VTT.
"""
    result = parse_subtitles(vtt_content)
    assert len(result) == 2
    assert result[0]["start_ms"] == 1500
    assert result[0]["end_ms"] == 4000
    assert result[0]["text"] == "Texto con identificador y estilo VTT."
    assert result[1]["start_ms"] == 5000
    assert result[1]["end_ms"] == 7500

def test_parse_subtitles_vtt_no_hours():
    vtt_content = """WEBVTT

01:20.500 --> 01:25.000
Segmento de audio en minuto 1.
"""
    result = parse_subtitles(vtt_content)
    assert len(result) == 1
    # 1 min 20.5 s = 80500 ms
    assert result[0]["start_ms"] == 80500
    # 1 min 25.0 s = 85000 ms
    assert result[0]["end_ms"] == 85000
    assert result[0]["duration_ms"] == 4500
    assert result[0]["text"] == "Segmento de audio en minuto 1."

def test_parse_subtitles_strips_html_and_ssa_tags():
    content = r"""1
00:00:01,000 --> 00:00:03,000
<b>Negrita</b>, <i>cursiva</i> y <font color="blue">azul</font> {\an8\pos(100,200)}con estilo ASS.
"""
    result = parse_subtitles(content)
    assert len(result) == 1
    assert result[0]["text"] == "Negrita, cursiva y azul con estilo ASS."

def test_parse_subtitles_sorting_unordered():
    unordered_srt = """2
00:00:06,000 --> 00:00:08,000
Mensaje tardío.

1
00:00:01,000 --> 00:00:03,000
Mensaje inicial.
"""
    result = parse_subtitles(unordered_srt)
    assert len(result) == 2
    assert result[0]["start_ms"] == 1000
    assert result[0]["index"] == 1
    assert result[0]["text"] == "Mensaje inicial."

    assert result[1]["start_ms"] == 6000
    assert result[1]["index"] == 2
    assert result[1]["text"] == "Mensaje tardío."

def test_parse_subtitles_filters_invalid_and_empty():
    invalid_content = """1
00:00:05,000 --> 00:00:02,000
Texto con fin anterior al inicio (invalido).

2
00:00:03,000 --> 00:00:03,000
Texto con duracion cero.

3
00:00:07,000 --> 00:00:09,000
<b>   </b>

4
00:00:10,000 --> 00:00:12,000
Texto valido final.
"""
    result = parse_subtitles(invalid_content)
    assert len(result) == 1
    assert result[0]["text"] == "Texto valido final."
    assert result[0]["index"] == 1

def test_parse_subtitles_empty_or_whitespace():
    assert parse_subtitles("") == []
    assert parse_subtitles("   \n\n  \t  ") == []
    assert parse_subtitles("Este texto no contiene subtítulos ni timestamps") == []
