# 🎙️ Voice-TTS Studio | Narración y Software Educativo

Servidor local de síntesis de voz (Text-to-Speech) de alta fidelidad, optimizado para **narraciones pedagógicas, cursos interactivos, doblaje de subtítulos y software educativo**.

Combina tres potentes motores con enrutamiento inteligente:
1. 🇲🇽 **Microsoft Edge Neural TTS** para español con calidad de estudio (0 MB VRAM).
2. 🇺🇸 **Kokoro-82M AI** acelerado por GPU (**NVIDIA CUDA**) para inglés cinematográfico con soporte de **Voice Blending**.
3. 🎭 **Xiaomi MiMo Speech Synthesis v2.5** en la nube con **Modo Director** y **Audio Tags** (`[laughter]`, `[sigh]`, `[whisper]`).

---

## ⚡ Características Principales

- 🇲🇽 **Español Docente (Microsoft Edge Neural)**:
  - Voces recomendadas: `es-MX-JorgeNeural` (Masculino, sereno y explicativo) y `es-MX-DaliaNeural` (Femenina, dicción cristalina).
  - Cero consumo de memoria VRAM (ultra-rápido y sin saturar tu tarjeta gráfica).
- 🇺🇸 **Inglés Educativo con Voice Blending (Kokoro-82M en GPU)**:
  - Soporte para **mezcla nativa de voces**: `af_bella,af_sarah` (la combinación de referencia para docencia y tutoriales), `af_heart` (insignia de Kokoro) y `am_adam` (narrador académico).
  - Acelerado por hardware con **NVIDIA CUDA** (optimizado para GPUs RTX 3050, consumiendo solo ~400 MB de VRAM).
- 🎭 **Xiaomi MiMo v2.5 (Modo Director y Audio Tags)**:
  - Control de entonación y emoción en lenguaje natural (`style_prompt`).
  - Etiquetas auditivas realistas integradas en el texto: `[laughter]`, `[sigh]`, `[whisper]`, etc.
- 🎬 **Doblaje y Sincronización de Subtítulos (.SRT / .VTT)**:
  - **Modo 'synced'**: Inserción de silencios y *time-stretch* preventivo para respetar exactamente las marcas temporales de un video.
  - **Modo 'continuous'**: Unificación fluida con pausas naturales estilo audiolibro.
- 🎵 **Formato MP3 Ligero por Defecto**:
  - Salida nativa en MP3 (192 kbps), reduciendo el peso en ~90% respecto a WAV sin perder fidelidad auditiva (con opción de salida WAV PCM).
- ⏱️ **Control de Ritmo Pedagógico**:
  - Velocidad predeterminada a **`0.95x`** (`-5%`), el tempo ideal para que los estudiantes asimilen conceptos complejos sin fatiga auditiva.
- ⏸️ **Etiquetas de Pausa Natural**:
  - Soporte para etiquetas `[pausa]` en los guiones, generando silencios naturales entre diapositivas o ideas clave.

---

## 📂 Arquitectura Modular del Proyecto

```
Voice-TTS/
├── app.py                  # Servidor API FastAPI (enrutador, validación y CORS)
├── catalog.py              # Catálogo curado de voces educativas (es / en)
├── subtitles.py            # Parser SRT/VTT, sincronización y time-stretch
├── engines/                # Motores de síntesis desacoplados
│   ├── __init__.py         # Re-exportador del paquete de motores
│   ├── edge_engine.py      # Motor Microsoft Edge Neural TTS
│   ├── kokoro_engine.py    # Motor Kokoro-82M en GPU (CUDA)
│   └── mimo_engine.py      # Motor Xiaomi MiMo v2.5 (Director Mode)
├── tests/                  # Suite de pruebas automatizadas (35 tests)
│   ├── test_subtitles.py   # Pruebas de parseo, sanitización y ordenamiento
│   ├── test_catalog_and_routing.py # Pruebas del catálogo y reglas de motor
│   ├── test_api_endpoints.py # Pruebas de endpoints REST y validaciones
│   ├── test_tts_engines.py # Pruebas unitarias de motores con mocks
│   └── test_live_smoke.py  # Pruebas de humo reales de extremo a extremo
├── run_tests.bat           # Ejecutor de pruebas en un clic para Windows
├── start_app.bat           # Inicia el Estudio Web en http://localhost:8000
├── requirements.txt        # Dependencias de producción
├── requirements-dev.txt    # Dependencias de testing (pytest, pytest-asyncio)
├── static/                 # Interfaz Web del Estudio de Locución
│   ├── index.html          # Panel de control y documentación integrada
│   ├── script.js           # Lógica del cliente, selector y reproductor
│   └── style.css           # Estilos visuales modernos
└── output/                 # Directorio de salida para audios generados
```

---

## 🚀 Inicio Rápido

### 1. Iniciar con un solo clic (Windows)
Haz doble clic en **`start_app.bat`**. 
Esto abrirá automáticamente tu navegador en `http://localhost:8000`.

### 2. Ejecutar la Suite de Pruebas
Haz doble clic en **`run_tests.bat`** o ejecuta desde la terminal:
```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```

### 3. Inicio manual desde la terminal
```bash
.venv\Scripts\activate
python -m uvicorn app:app --port 8000 --host 127.0.0.1 --reload
```

---

## 📡 Documentación de la API

### 1. Endpoint Principal de Síntesis
**`POST http://localhost:8000/api/tts`**

#### Headers:
`Content-Type: application/json`

#### Ejemplo en Español (Edge-TTS):
```json
{
  "text": "Bienvenidos a esta lección sobre metodología clínica. [pausa] Hoy revisaremos el formato PICO.",
  "voice": "es-MX-JorgeNeural",
  "speed": 0.95,
  "format": "mp3"
}
```

#### Ejemplo en Inglés con Mezcla Educativa (Kokoro AI GPU):
```json
{
  "text": "Welcome to this educational session. [pausa] Please follow along with the interactive guide.",
  "voice": "af_bella,af_sarah",
  "speed": 0.95,
  "format": "mp3"
}
```

#### Ejemplo con Xiaomi MiMo (Modo Director + Audio Tags):
```json
{
  "text": "That was an astonishing result! [laughter] Let's inspect the final data step by step.",
  "voice": "mimo-Chloe",
  "style_prompt": "Enthusiastic and energetic teaching tone",
  "speed": 0.95
}
```

### 2. Endpoint de Doblaje de Subtítulos
**`POST http://localhost:8000/api/tts/subtitle`**

```json
{
  "subtitle_text": "1\n00:00:00,500 --> 00:00:03,500\nPrimera frase.\n\n2\n00:00:04,000 --> 00:00:07,000\nSegunda frase.",
  "voice": "es-MX-JorgeNeural",
  "mode": "synced",
  "speed": 1.0,
  "format": "mp3"
}
```

---

## 🎓 Voces y Mezclas Recomendadas para Software Educativo

| Idioma | ID de Voz | Motor | Perfil de Locución |
| :--- | :--- | :--- | :--- |
| **Español** | `es-MX-JorgeNeural` | Edge Neural | ⭐ **Recomendado Docente**. Tono sereno, confiable y explicativo. |
| **Español** | `es-MX-DaliaNeural` | Edge Neural | ⭐ **Recomendada Docente**. Dicción limpia y cercana para lecciones. |
| **Español** | `ef_dora,af_sarah` | Kokoro GPU | ⭐ **Mezcla Educativa Kokoro**. Dora en español + cadencia pedagógica de Sarah. |
| **Inglés** | `af_bella,af_sarah` | Kokoro GPU | ⭐ **Mezcla Educativa Insignia**. Articulación de Bella + cadencia de Sarah. |
| **Inglés** | `af_heart` | Kokoro GPU | ⭐ **Insignia Kokoro**. Voz cálida, empática y de máxima fidelidad humana. |
| **Inglés** | `mimo-Chloe` | MiMo Cloud | ⭐ **Modo Director**. Expresividad cinematográfica y Audio Tags. |
| **Inglés** | `am_adam` | Kokoro GPU | ⭐ **Narrador Académico**. Estilo documental y conferencias. |

---

## 📄 Licencia
Proyecto distribuido bajo la licencia MIT.
