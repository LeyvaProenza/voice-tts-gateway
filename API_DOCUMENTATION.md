# 📘 Guía de Integración de API - Voice-TTS Gateway

Esta guía está diseñada para que cualquier otro proyecto (scripts de automatización, agentes de IA, aplicaciones web, bots o herramientas de PowerPoint/video) pueda consumir fácilmente los servicios de síntesis de voz locales.

---

## 🌐 Información del Servidor

* **URL Base Local**: `http://localhost:8000`
* **Protocolo**: HTTP / REST (OpenAPI)
* **Formato de Solicitud**: JSON (`Content-Type: application/json`)
* **Formato de Audio por Omisión**: `audio/mpeg` (MP3 192 kbps, ~8-10x más ligero) o `audio/wav` (WAV PCM 16-bit)

---

## ⚡ 1. Resumen de Motores y Voces

El servidor cuenta con enrutamiento inteligente automático:

| Idioma | Motor Activo | Voces Destacadas | Uso de GPU | Recomendación de Uso |
| :--- | :--- | :--- | :--- | :--- |
| **Español** | Microsoft Edge Neural | `es-MX-JorgeNeural` (Masculino)<br>`es-MX-DaliaNeural` (Femenino) | 0 MB VRAM | Narración educativa, clases y cursos en español con dicción impecable. |
| **Inglés** | **Kokoro-82M AI** | `af_heart` (Insignia Kokoro)<br>`af_bella,af_sarah` (Mezcla Educativa)<br>`am_adam` (Docente US) | ~400 MB VRAM (CUDA) | Locución en inglés de calidad cinematográfica, soporte nativo de **Voice Blending**. |

---

## 🎛️ 2. Mezcla de Voces en Kokoro (Voice Blending)

Kokoro-82M cuenta con soporte nativo para **combinar dos o más voces**. 

### ¿Cómo funciona internamente?
Las voces en Kokoro son vectores de estilo (*style embeddings*). Al solicitar una combinación separada por comas (por ejemplo: `af_bella,af_sarah`), el motor carga los tensores de cada voz y calcula su media matemática:
`self.voices[voice] = torch.mean(torch.stack(packs), dim=0)`

### Mezclas Educativas Recomendadas:
1. **`af_bella,af_sarah` (La combinación de referencia para e-learning)**:
   - **Bella**: Aporta articulación nítida, energía y claridad en las consonantes.
   - **Sarah**: Aporta un ritmo pausado, calidez y cadencia instruccional natural.
   - **Resultado**: La voz más clara y equilibrada para tutoriales técnicos, narración de diapositivas y vídeos de formación en inglés.
2. **`af_heart,af_nicole`**:
   - Calidez humana y empatía fusionada con dicción metódica para tutoriales paso a paso.
3. **`am_adam,am_michael`**:
   - Tono documental masculino sobrio y formal para lecciones científicas o conferencias magistrales.

### Ponderación de Mezclas (Ratios Personalizados):
Kokoro permite repetir nombres en la lista separada por comas para otorgar mayor peso a una voz:
- `af_bella,af_bella,af_sarah` → **66.6% Bella / 33.3% Sarah** (Más enérgica).
- `af_bella,af_sarah,af_sarah` → **33.3% Bella / 66.6% Sarah** (Más pausada y cálida).

Cualquier combinación válida separada por comas es aceptada automáticamente por el servidor.

---

## 📡 3. Endpoints Disponibles

### A. Sintetizar Texto a Audio (Principal)
`POST /api/tts`

#### Parámetros del Body (JSON):
| Campo | Tipo | Obligatorio | Por Omisión | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **`text`** | string | **Sí** | - | Texto a narrar. Admite etiquetas `[pausa]` para insertar respiros naturales. |
| **`voice`** | string | No | `"es-MX-JorgeNeural"` | ID de la voz individual (ej. `es-MX-JorgeNeural`, `af_heart`) o mezcla separada por comas (ej. `af_bella,af_sarah`). |
| **`speed`** | float | No | `0.95` | Velocidad de habla. `0.95` es el ritmo pedagógico recomendado (`0.75` a `1.25`). |
| **`format`** | string | No | `"mp3"` | Formato de salida: `"mp3"` (recomendado, ultra ligero) o `"wav"`. |
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

## 💻 4. Ejemplos de Código Listos para Copiar y Pegar

### 🐍 Python (Ideal para scripts de IA o Backend)

```python
import requests

def generar_audio_educativo(texto, voz="es-MX-JorgeNeural", velocidad=0.95, formato="mp3", archivo_salida="leccion.mp3"):
    url = "http://localhost:8000/api/tts"
    payload = {
        "text": texto,
        "voice": voz,
        "speed": velocidad,
        "format": formato
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        with open(archivo_salida, "wb") as f:
            f.write(response.content)
        print(f"✅ Audio {formato.upper()} guardado exitosamente en: {archivo_salida}")
        return True
    else:
        print(f"❌ Error ({response.status_code}): {response.text}")
        return False

# --- Ejemplos de Uso ---

# 1. Narración en Español en MP3 (Edge-TTS)
generar_audio_educativo(
    texto="Bienvenidos al módulo clínico. [pausa] Hoy revisaremos el consentimiento informado.",
    voz="es-MX-JorgeNeural",
    velocidad=0.95,
    formato="mp3",
    archivo_salida="leccion_espanol.mp3"
)

# 2. Narración en Inglés con MEZCLA EDUCATIVA (Bella + Sarah en Kokoro GPU)
generar_audio_educativo(
    texto="Welcome to this interactive session. [pausa] We will explore foundational research concepts step by step.",
    voz="af_bella,af_sarah",
    velocidad=0.95,
    formato="mp3",
    archivo_salida="lesson_bella_sarah.mp3"
)

# 3. Narración en Inglés con Voz Insignia Individual (Heart en Kokoro GPU)
generar_audio_educativo(
    texto="Artificial intelligence enables educators to personalize learning at scale.",
    voz="af_heart",
    velocidad=0.95,
    formato="mp3",
    archivo_salida="lesson_heart.mp3"
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
        [string]$Format = "mp3",
        [string]$OutputFile = "narracion.mp3"
    )

    $url = "http://localhost:8000/api/tts"
    $body = @{
        text   = $Text
        voice  = $Voice
        speed  = $Speed
        format = $Format
    } | ConvertTo-Json -Compress

    Write-Host "Generando narración con voz: $Voice (Formato: $Format)..."
    
    Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -OutFile $OutputFile
    
    Write-Host "Audio guardado en: $OutputFile"
}

# Ejemplos de llamada:
Invoke-VoiceTTS -Text "Hola a todos. [pausa] Esta es una diapositiva automatizada." -Voice "es-MX-JorgeNeural" -OutputFile "slide_1.mp3"
Invoke-VoiceTTS -Text "This slide is narrated with the Bella and Sarah educational blend." -Voice "af_bella,af_sarah" -OutputFile "slide_en.mp3"
```

---

### 🌐 JavaScript / Node.js / Fetch (Para Apps Web)

```javascript
async function sintetizarAudio(texto, voz = 'af_bella,af_sarah', formato = 'mp3', velocidad = 0.95) {
    const response = await fetch('http://localhost:8000/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: texto,
            voice: voz,
            speed: velocidad,
            format: formato
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
# Ejemplo de Mezcla Educativa Bella & Sarah en MP3:
curl -X POST http://localhost:8000/api/tts \
     -H "Content-Type: application/json" \
     -d "{\"text\":\"Welcome students. Kokoro is blending Bella and Sarah.\", \"voice\":\"af_bella,af_sarah\", \"format\":\"mp3\"}" \
     --output blend_test.mp3

# Ejemplo en Español con Jorge:
curl -X POST http://localhost:8000/api/tts \
     -H "Content-Type: application/json" \
     -d "{\"text\":\"Hola mundo educativo. [pausa] Todo funcionando.\", \"voice\":\"es-MX-JorgeNeural\", \"format\":\"mp3\"}" \
     --output prueba_es.mp3
```

---

## 🎯 5. Catálogo Completo de Voces

### 🇲🇽 Español (Microsoft Edge Neural)
* **`es-MX-JorgeNeural`** *(⭐ Recomendado Docente Masculino)*: Tono sereno, claro y explicativo.
* **`es-MX-DaliaNeural`** *(⭐ Recomendada Docente Femenina)*: Expresiva, cálida y didáctica.
* `es-CO-GonzaloNeural` *(Colombia, masculino neutro y formal).*
* `es-CO-SalomeNeural` *(Colombia, femenino pausado).*
* `es-AR-TomasNeural` *(Argentina, locución segura).*
* `es-CL-CatalinaNeural` *(Chile, didáctica y expresiva).*
* `es-US-AlonsoNeural` *(Latino Neutro EE.UU., dinámico).*
* `es-US-PalomaNeural` *(Latino Neutro EE.UU., joven y fresco).*
* `es-ES-AlvaroNeural` *(España peninsular formal).*
* `es-ES-ElviraNeural` *(España peninsular clásico).*

### 🇺🇸 Inglés (Kokoro-82M AI en GPU)

#### ⭐ Mezclas Educativas Recomendadas (Voice Blends)
* **`af_bella,af_sarah`** *(⭐ La mezcla ideal para educadores)*: Articulación nítida de Bella + cadencia y calidez pedagógica de Sarah.
* **`af_heart,af_nicole`**: Fusión de calidez humana con tono instructivo metódico.
* **`am_adam,am_michael`**: Narrador masculino sobrio para lecciones científicas o conferencias magistrales.

#### American Female (11 Voces)
* **`af_heart`** *(⭐ Insignia Kokoro)*: Calidez humana insuperable y máxima naturalidad para e-learning.
* `af_bella`: Articulada, enérgica y didáctica.
* `af_sarah`: Juvenil, cadenciosa y afable.
* `af_nicole`: Paciente y técnica.
* `af_alloy`: Versátil y moderna.
* `af_aoede`: Suave y envolvente.
* `af_jessica`: Locución clara y formal para presentaciones.
* `af_kore`: Calma y reflexiva.
* `af_nova`: Dinámica y motivacional.
* `af_river`: Textura acústica contemporánea.
* `af_sky`: Luminosa y positiva.

#### American Male (9 Voces)
* **`am_adam`** *(⭐ Recomendado Docente)*: Clásico documental y conferencias.
* `am_michael`: Maduro y técnico para ciencia.
* `am_echo`: Pausado y reflexivo.
* `am_eric`: Conversacional y cercano.
* `am_fenrir`: Grave y resonante.
* `am_liam`: Dinámico y juvenil.
* `am_onyx`: Autorizado y sobrio.
* `am_puck`: Ágil y espontáneo.
* `am_santa`: Cálido y festivo.

#### British Female (4 Voces)
* **`bf_emma`** *(⭐ Recomendada UK)*: Acento británico elegante y pedagógico.
* `bf_alice`: Articulada y refinada.
* `bf_isabella`: Formal y suave.
* `bf_lily`: Joven, clara y melodiosa.

#### British Male (4 Voces)
* **`bm_george`** *(⭐ Recomendado UK)*: Presencia autorizada y catedrática.
* `bm_daniel`: Sobrio y catedrático.
* `bm_fable`: Estilo narrador literario.
* `bm_lewis`: Preciso y nítido.

---

## 💡 6. Consejos Pedagógicos y Rendimiento
1. **Ritmo de Explicación**: Mantén `speed: 0.95` para explicaciones estándar y `speed: 0.90` si estás presentando fórmulas o terminología compleja.
2. **Pausas Estratégicas**: Usa `[pausa]` entre ideas clave para dar un respiro cognitivo al estudiante.
3. **Formato Ligero MP3**: El formato por omisión es MP3 (`192 kbps`), el cual reduce el peso de audio en un ~90% respecto a WAV sin pérdida perceptible, ideal para cursos y web.
4. **Mezclas Ilimitadas**: Puedes probar combinaciones personalizadas separando cualquier voz con comas (ej. `"af_bella,af_sarah"` o `"af_heart,af_bella"`). Kokoro calculará el promedio vectorial en tiempo real en tu GPU.
