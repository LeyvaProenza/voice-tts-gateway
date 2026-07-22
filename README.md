# 🎙️ Voice-TTS Gateway & Control Panel

Servidor local de síntesis y clonación de voz (**Text-to-Speech**) basado en **XTTSv2** (con aceleración GPU CUDA) e integración nativa con **Microsoft Edge Neural TTS**. Incluye un **API Gateway en FastAPI** y un **Panel de Control Web** interactivo.

Desarrollado para conectarse directamente con clientes de IA o aplicaciones externas como **Antigravity**, permitiendo generar audios de alta fidelidad a partir de texto.

---

## ⚡ Características Principales

- 🧠 **Motor Doble de TTS**:
  - **XTTSv2 Local**: Clonación de voz de alta fidelidad a partir de muestras `.wav` de 3 a 10 segundos (acelerado por GPU con PyTorch/CUDA).
  - **Edge Neural TTS Directo**: Bypass automático para voces neurales ultra-claras (ej. `es-MX-JorgeNeural`, `es-MX-DaliaNeural`) con calidad de estudio y respuesta instantánea.
- 🎛️ **Panel de Control Web (Dashboard)**:
  - Control en tiempo real del estado del servidor XTTS (`Activo` / `Desconectado`).
  - Botones para encender/apagar la GPU y consultar logs en vivo.
  - Gestión Drag & Drop de voces de referencia (`.wav`).
  - Preescucha de muestras de audio y prueba rápida de síntesis.
- 🇲🇽 **Filtro de Seseo Latinoamericano**:
  - Opción `remove_ceceo` para adaptar automáticamente ortografías con ceceo castellano (`z`, `ce`, `ci`) a seseo latinoamericano (`s`, `se`, `si`), evitando pronunciaciones en "th" con modelos en español europeo.
- 🔌 **API REST OpenAPI / Swagger**:
  - Endpoint unificado `POST /api/tts` que devuelve el stream del archivo `.wav` directamente para su integración en automatizaciones o canalizaciones de video/powerpoint.

---

## 📂 Estructura del Proyecto

```
Voice-TTS/
├── app.py              # API Gateway FastAPI & Panel de Control Backend
├── start_app.bat       # Script batch para iniciar el Panel de Control Web (puerto 8000)
├── start_tts.bat       # Script batch para iniciar solo el motor XTTS (puerto 8020)
├── stop_tts.bat        # Script batch para detener el servidor XTTS y liberar la GPU
├── requirements.txt    # Lista de dependencias del proyecto
├── .gitignore          # Reglas de exclusión de Git (excluye pesos de modelo y venv)
├── README.md           # Documentación principal para GitHub
├── static/             # Frontend del Panel de Control Web
│   ├── index.html      # Estructura del dashboard
│   ├── script.js       # Lógica del cliente y llamadas a la API
│   └── style.css       # Estilos visuales del panel
├── speakers/           # Colección de archivos .wav de referencia para clonación
├── models/             # Pesos del modelo XTTSv2 (descargados automáticamente)
└── output/             # Directorio de salida para audios sintetizados
```

---

## 🚀 Inicio Rápido

### Requisitos Previos
- **Python**: v3.10 o superior.
- **FFmpeg**: Instalado y añadido al PATH del sistema (necesario para procesamiento de audio con `pydub`).
- **NVIDIA GPU** (Opcional pero recomendado): Con controladores CUDA 12.1+ para síntesis en tiempo real con XTTS.

### Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/TU_USUARIO/Voice-TTS.git
   cd Voice-TTS
   ```

2. **Crear e inicializar el entorno virtual**:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🖥️ Uso del Panel de Control Web

Para iniciar el servidor gateway y abrir la interfaz gráfica:

```bash
# Ejecutar el script batch en Windows:
start_app.bat
```

O manualmente con Uvicorn:
```bash
uvicorn app:app --port 8000 --host 127.0.0.1
```

Abre tu navegador en `http://localhost:8000`. Desde el panel podrás:
- Encender el servidor local XTTS con un solo clic.
- Subir archivos `.wav` de referencia para clonar voces.
- Probar la síntesis de texto en tiempo real.

---

## 📡 Documentación de la API

### Endpoint Principal de Síntesis
**`POST /api/tts`**

#### Headers:
`Content-Type: application/json`

#### Cuerpo de la Solicitud (JSON):
```json
{
  "text": "Texto a sintetizar en audio.",
  "speaker_wav": "es-MX-JorgeNeural.wav",
  "language": "es",
  "temperature": 0.75,
  "length_penalty": 1.0,
  "repetition_penalty": 5.0,
  "top_k": 50,
  "top_p": 0.85,
  "remove_ceceo": true
}
```

#### Respuesta:
- **Content-Type**: `audio/wav`
- **Body**: Stream binario del archivo `.wav` listo para reproducir o guardar.

#### Ejemplo de uso con cURL:
```bash
curl -X POST http://localhost:8000/api/tts \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Hola, este es un mensaje de prueba sintetizado localmente.",
           "speaker_wav": "es-MX-JorgeNeural.wav",
           "language": "es"
         }' \
     --output mi_audio.wav
```

### Otros Endpoints Disponibles

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Estado del servidor XTTS (`connected` / `disconnected`). |
| `POST` | `/api/server/start` | Enciende el subproceso del servidor XTTS (GPU). |
| `POST` | `/api/server/stop` | Apaga el servidor XTTS y libera la VRAM. |
| `GET` | `/api/server/log` | Consulta las últimas líneas del archivo de log. |
| `GET` | `/api/speakers` | Lista las voces de referencia disponibles en `speakers/`. |
| `POST` | `/api/speakers/upload` | Sube un nuevo archivo de voz `.wav`. |
| `DELETE` | `/api/speakers/{filename}` | Elimina un archivo de voz de referencia. |

---

## 📄 Licencia

Proyecto distribuido bajo la licencia MIT. Libre para uso personal, educativo y comercial.
