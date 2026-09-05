# 📘 Guía de Integración de API - Voice-TTS Gateway

Esta guía está diseñada para que cualquier otro proyecto (scripts de automatización, agentes de IA, aplicaciones web, bots o herramientas de PowerPoint/video) pueda consumir fácilmente los servicios de síntesis de voz locales.

---

## 🌐 Información del Servidor

* **URL Base Local**: `http://localhost:8000`
* **Protocolo**: HTTP / REST (OpenAPI)
* **Formato de Solicitud**: JSON (`Content-Type: application/json`)
* **Formato de Respuesta de Audio**: `audio/wav` (Binario WAV PCM 16-bit, 24000 Hz, Mono)

---

## ⚡ 1. Resumen Rápido de Motores y Voces

El servidor cuenta con enrutamiento inteligente automático:

| Idioma | Motor Activo | Voces Destacadas | Uso de GPU | Recomendación de Uso |
| :--- | :--- | :--- | :--- | :--- |
| **Español** | Microsoft Edge Neural | `es-MX-JorgeNeural` (Masculino)<br>`es-MX-DaliaNeural` (Femenino) | 0 MB VRAM | Narración educativa, clases y cursos en español. |
| **Inglés** | **Kokoro-82M AI** | `af_heart` (Femenino)<br>`am_adam` (Masculino)<br>`bf_emma` (Femenino UK) | ~400 MB VRAM (CUDA) | Locución en inglés de calidad cinematográfica y e-learning. |

---

## 📡 2. Endpoints Disponibles

### A. Sintetizar Texto a Audio (Principal)
`POST /api/tts`

#### Parámetros del Body (JSON):
| Campo | Tipo | Obligatorio | Por Omisión | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **`text`** | string | **Sí** | - | Texto a narrar. Admite etiquetas `[pausa]` para insertar respiros naturales. |
| **`voice`** | string | No | `"es-MX-JorgeNeural"` | ID de la voz a utilizar (ej. `es-MX-JorgeNeural`, `af_heart`, `am_adam`). |
| **`speed`** | float | No | `0.95` | Velocidad de habla. `0.95` es el ritmo pedagógico recomendado (`0.75` a `1.25`). |
| **`language`** | string | No | Auto | `"es"` o `"en"` (se autodetecta según la voz si se omite). |

---

### B. Listar Catálogo Completo de Voces
`GET /api/voices`

Devuelve un JSON con todas las voces agrupadas por idioma (`es` y `en`), incluyendo género, acento y descripción pedagógica.

---

### C. Estado del Servidor y GPU
`GET /api/status`

Devuelve el estado de conexión y si la GPU (RTX 3050 con CUDA) está activa para Kokoro.

---

## 💻 3. Ejemplos de Código Listos para Copiar y Pegar

### 🐍 Python (Ideal para scripts de IA o Backend)

```python
import requests

def generar_audio_educativo(texto, voz="es-MX-JorgeNeural", velocidad=0.95, archivo_salida="leccion.wav"):
    url = "http://localhost:8000/api/tts"
    payload = {
        "text": texto,
        "voice": voz,
        "speed": velocidad
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        with open(archivo_salida, "wb") as f:
            f.write(response.content)
        print(f"✅ Audio guardado exitosamente en: {archivo_salida}")
        return True
    else:
        print(f"❌ Error ({response.status_code}): {response.text}")
        return False

# --- Ejemplos de Uso ---

# 1. Narración en Español (Edge-TTS)
generar_audio_educativo(
    texto="Bienvenidos al módulo clínico. [pausa] Hoy revisaremos el consentimiento informado.",
    voz="es-MX-JorgeNeural",
    velocidad=0.95,
    archivo_salida="leccion_espanol.wav"
)

# 2. Narración en Inglés (Kokoro AI con GPU)
generar_audio_educativo(
    texto="Welcome to this artificial intelligence tutorial. [pausa] Follow the instructions on screen.",
    voz="af_heart",
    velocidad=0.95,
    archivo_salida="lesson_english.wav"
)
```

---

### 💻 PowerShell (Ideal para automatizar PowerPoint y videos en Windows)

```powershell
function Invoke-VoiceTTS {
    param (
        [Parameter(Mandatory=$true)][string]$Text,
        [string]$Voice = "es-MX-JorgeNeural",
        [double]$Speed = 0.95,
        [string]$OutputFile = "narracion.wav"
    )

    $url = "http://localhost:8000/api/tts"
    $body = @{
        text  = $Text
        voice = $Voice
        speed = $Speed
    } | ConvertTo-Json -Compress

    Write-Host "Generando narración con voz: $Voice..."
    
    Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -OutFile $OutputFile
    
    Write-Host "Audio guardado en: $OutputFile"
}

# Ejemplo de llamada:
Invoke-VoiceTTS -Text "Hola a todos. [pausa] Esta es una diapositiva automatizada." -Voice "es-MX-JorgeNeural" -OutputFile "slide_1.wav"
Invoke-VoiceTTS -Text "Hello, this slide was generated with Kokoro AI." -Voice "af_heart" -OutputFile "slide_en.wav"
```

---

### 🌐 JavaScript / Node.js / Fetch (Para Apps Web)

```javascript
async function sintetizarAudio(texto, voz = 'es-MX-JorgeNeural', velocidad = 0.95) {
    const response = await fetch('http://localhost:8000/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: texto,
            voice: voz,
            speed: velocidad
        })
    });

    if (!response.ok) {
        throw new Error(`Error en el servidor: ${response.statusText}`);
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    
    // Reproducir directamente en el navegador:
    const audio = new Audio(audioUrl);
    audio.play();
    
    return audioBlob;
}
```

---

### 🖥️ cURL (Línea de comandos rápida)

```bash
# Ejemplo en Español con Jorge:
curl -X POST http://localhost:8000/api/tts \
     -H "Content-Type: application/json" \
     -d "{\"text\":\"Hola mundo educativo. [pausa] Todo funcionando.\", \"voice\":\"es-MX-JorgeNeural\", \"speed\":0.95}" \
     --output prueba_es.wav

# Ejemplo en Inglés con Kokoro AI (Heart):
curl -X POST http://localhost:8000/api/tts \
     -H "Content-Type: application/json" \
     -d "{\"text\":\"Hello students. Kokoro is generating this voice locally.\", \"voice\":\"af_heart\", \"speed\":0.95}" \
     --output prueba_en.wav
```

---

## 🎯 4. Catálogo Rápido de IDs de Voces

### 🇲🇽 Español (Microsoft Edge Neural)
* **`es-MX-JorgeNeural`** *(Recomendado Docente Masculino)*: Tono sereno y claro.
* **`es-MX-DaliaNeural`** *(Recomendada Docente Femenina)*: Expresiva y didáctica.
* `es-CO-GonzaloNeural` *(Masculino Colombia, formal).*
* `es-CO-SalomeNeural` *(Femenino Colombia, suave).*
* `es-US-AlonsoNeural` *(Masculino neutro internacional).*
* `es-ES-AlvaroNeural` *(Masculino España peninsular).*

### 🇺🇸 Inglés (Kokoro-82M AI en GPU)
* **`af_heart`** *(Recomendada Femenina US)*: Calidez humana insuperable, ritmo empático.
* **`am_adam`** *(Recomendado Masculino US)*: Tono clásico documental/académico.
* `af_bella` *(Femenina US, dinámica).*
* `af_nicole` *(Femenina US, paciente y técnica).*
* `am_michael` *(Masculino US, sobrio).*
* `bf_emma` *(Femenina British, acento académico elegante).*
* `bm_george` *(Masculino British, narrador formal).*

---

## 💡 5. Consejos Pedagógicos
1. **Ritmo de Explicación**: Mantén `speed: 0.95` para explicaciones normales y `speed: 0.90` si estás presentando fórmulas o terminología científica compleja.
2. **Pausas Estratégicas**: Usa `[pausa]` entre ideas clave para dar un respiro al oyente.
3. **Persistencia**: La respuesta es un archivo binario `.wav` estándar que no requiere transcodificación previa para reproducirse en navegadores, reproductores del sistema operativo o insertarse en PowerPoint con scripts COM.
