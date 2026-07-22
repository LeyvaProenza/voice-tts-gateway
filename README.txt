========================================================================
             Voice-TTS Gateway - Servidor de Clonacion de Voz
========================================================================

Este proyecto es un servidor local de clonacion de voz (Text-To-Speech)
con XTTSv2, optimizado para GPU NVIDIA (CUDA 12.1).

Expone una API REST que Antigravity puede llamar para enviar texto
y recibir audio WAV generado con la voz clonada.

------------------------------------------------------------------------
ESTRUCTURA DEL PROYECTO
------------------------------------------------------------------------
  speakers/      Archivos .wav de referencia para clonar voces (3-10 seg)
  models/        Modelo XTTSv2 (se descarga automaticamente, ~2.4 GB)
  output/        Carpeta de salida (para pruebas)
  static/        Interfaz web del panel de control
  app.py         Servidor FastAPI (gateway + panel de control)
  start_app.bat  Inicia el panel de control (puerto 8000)
  start_tts.bat  Inicia solo el servidor XTTS (puerto 8020)
  stop_tts.bat   Detiene el servidor XTTS
  .venv/         Entorno virtual Python con todas las dependencias

------------------------------------------------------------------------
COMO USAR
------------------------------------------------------------------------

OPCION A - Panel de Control Web (recomendado):

  1. Doble clic en 'start_app.bat'
     - Abre automaticamente http://localhost:8000 en tu navegador
     - Desde la interfaz puedes:
       * Encender/apagar el servidor XTTS con un boton
       * Subir archivos .wav de referencia (drag & drop)
       * Ver/eliminar/escuchar las voces cargadas
       * Hacer pruebas rapidas de sintesis
       * Ver la documentacion de la API para Antigravity

  2. En Antigravity, configura el endpoint:
       POST http://localhost:8000/api/tts

OPCION B - Solo el servidor XTTS (sin panel web):

  1. Doble clic en 'start_tts.bat'
  2. Doble clic en 'stop_tts.bat' para apagar

------------------------------------------------------------------------
API PARA ANTIGRAVITY
------------------------------------------------------------------------

Endpoint:   POST http://localhost:8000/api/tts
Content-Type: application/json

Request Body:
  {
    "text": "Texto a sintetizar",
    "speaker_wav": "nombre_del_archivo.wav",
    "language": "es",
    "temperature": 0.75,          // Opcional (por omisión: 0.75)
    "length_penalty": 1.0,        // Opcional (por omisión: 1.0)
    "repetition_penalty": 5.0,    // Opcional (por omisión: 5.0)
    "top_k": 50,                  // Opcional (por omisión: 50)
    "top_p": 0.85                 // Opcional (por omisión: 0.85)
  }

Response:
  - Content-Type: audio/wav
  - Body: bytes del archivo WAV generado
  - Guardar directamente como archivo .wav

Ejemplo con curl:
  curl -X POST http://localhost:8000/api/tts ^
       -H "Content-Type: application/json" ^
       -d "{\"text\":\"Hola mundo\",\"speaker_wav\":\"es-MX-DaliaNeural.wav\",\"language\":\"es\"}" ^
       --output salida.wav

------------------------------------------------------------------------
OTROS ENDPOINTS DISPONIBLES
------------------------------------------------------------------------

  GET  /api/status            Estado del servidor XTTS
  POST /api/server/start      Encender servidor XTTS
  POST /api/server/stop       Apagar servidor XTTS
  GET  /api/server/log        Ver log del servidor
  GET  /api/speakers          Listar voces disponibles
  POST /api/speakers/upload   Subir nueva voz (.wav)
  DEL  /api/speakers/{name}   Eliminar una voz

------------------------------------------------------------------------
VOCES DE REFERENCIA
------------------------------------------------------------------------

Requisitos del archivo .wav:
  - Formato: WAV (PCM, Mono, 22050-24000 Hz, 16-bit)
  - Duracion: 3 a 10 segundos
  - Audio limpio: sin ruido de fondo, eco ni musica
  - Una sola persona hablando de forma clara

Voces incluidas de ejemplo:
  - es-MX-DaliaNeural.wav   (Femenina, espanol mexicano)
  - es-MX-JorgeNeural.wav   (Masculino, espanol mexicano)
