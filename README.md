# 🎙️ Voice-TTS Studio | Narración y Software Educativo

Servidor local de síntesis de voz (Text-to-Speech) de alta fidelidad, optimizado para **narraciones pedagógicas, cursos interactivos y software educativo**.

Combina **Microsoft Edge Neural TTS** para español con calidad de estudio y **Kokoro-82M** acelerado por GPU (**NVIDIA CUDA**) para inglés con cadencia cinematográfica humana.

---

## ⚡ Características Principales

- 🇲🇽 **Español Docente (Microsoft Edge Neural)**:
  - Voces recomendadas: `es-MX-JorgeNeural` (Masculino, sereno y explicativo) y `es-MX-DaliaNeural` (Femenina, dicción cristalina).
  - Cero consumo de memoria VRAM (ultra-rápido y sin saturar tu tarjeta gráfica).
- 🇺🇸 **Inglés Educativo (Kokoro-82M en GPU)**:
  - Voces recomendadas: `af_heart` (la voz insignia de Kokoro, cálida y empática para e-learning) y `am_adam` (narrador documental académico).
  - Acelerado por hardware con **NVIDIA CUDA** (optimizado para GPUs RTX 3050 de 6 GB, consumiendo solo ~400 MB de VRAM).
- ⏱️ **Control de Ritmo Pedagógico**:
  - Ajuste de velocidad predeterminado a **`0.95x`** (`-5%`), el tempo ideal para que los estudiantes asimilen conceptos complejos sin fatiga auditiva.
- ⏸️ **Etiquetas de Pausa Natural**:
  - Soporte para etiquetas `[pausa]` en los guiones, generando silencios naturales entre diapositivas o ideas clave.
- 🔌 **API REST Unificada para Antigravity**:
  - Endpoint `POST /api/tts` que devuelve el stream del archivo `.wav` (PCM 16-bit) listo para reproducir o insertar directamente en diapositivas o videos.

---

## 📂 Estructura del Proyecto

```
Voice-TTS/
├── app.py              # Servidor API FastAPI con motores Edge-TTS y Kokoro AI
├── start_app.bat       # Inicia el Estudio Web en http://localhost:8000
├── requirements.txt    # Dependencias del proyecto
├── .gitignore          # Reglas de exclusión de Git
├── README.md           # Documentación del proyecto
├── static/             # Interfaz web del Estudio de Locución
│   ├── index.html      # Estructura del panel
│   ├── script.js       # Lógica del cliente y reproductor
│   └── style.css       # Estilos visuales modernos
└── output/             # Directorio de salida para audios generados
```

---

## 🚀 Inicio Rápido

### 1. Iniciar con un solo clic (Windows)
Haz doble clic en **`start_app.bat`**. 
Esto abrirá automáticamente tu navegador en `http://localhost:8000`.

### 2. Inicio manual desde la terminal
```bash
.venv\Scripts\activate
python -m uvicorn app:app --port 8000 --host 127.0.0.1
```

---

## 📡 Documentación de la API

### Endpoint Principal de Síntesis
**`POST http://localhost:8000/api/tts`**

#### Headers:
`Content-Type: application/json`

#### Ejemplo en Español (Edge-TTS):
```json
{
  "text": "Bienvenidos a esta lección sobre metodología clínica. [pausa] Hoy revisaremos el formato PICO.",
  "voice": "es-MX-JorgeNeural",
  "speed": 0.95
}
```

#### Ejemplo en Inglés (Kokoro AI):
```json
{
  "text": "Welcome to this educational session. [pausa] Please follow along with the interactive guide.",
  "voice": "af_heart",
  "speed": 0.95
}
```

#### Respuesta:
- **HTTP Status**: `200 OK`
- **Content-Type**: `audio/wav`
- **Body**: Stream binario del archivo WAV (PCM 16-bit).

---

## 🎓 Voces Recomendadas para Software Educativo

| Idioma | ID de Voz | Género | Acento | Perfil de Locución |
| :--- | :--- | :--- | :--- | :--- |
| **Español** | `es-MX-JorgeNeural` | Masculino | México | ⭐ **Recomendado**. Tono sereno, confiable y explicativo. |
| **Español** | `es-MX-DaliaNeural` | Femenino | México | ⭐ **Recomendada**. Dicción limpia y cercana para lecciones. |
| **Español** | `es-CO-GonzaloNeural` | Masculino | Colombia | Formal y neutro, ideal para lecturas científicas. |
| **Inglés** | `af_heart` | Femenino | American | ⭐ **Recomendada**. Voz cálida, empática y de máxima fidelidad. |
| **Inglés** | `am_adam` | Masculino | American | ⭐ **Recomendado**. Narrador estilo documental y conferencias. |
| **Inglés** | `bf_emma` | Femenino | British | Acento británico académico y elegante. |

---

## 📄 Licencia
Proyecto distribuido bajo la licencia MIT.
