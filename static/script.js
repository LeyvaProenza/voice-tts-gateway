// Voice-TTS Studio - Educational Narration Client

document.addEventListener('DOMContentLoaded', () => {
    // State
    let catalog = { es: [], en: [] };
    let currentLang = 'es';
    let currentSpeed = 0.95;
    let currentAudioUrl = null;

    // DOM Elements
    const langTabs = document.querySelectorAll('.lang-tab');
    const voiceSelect = document.getElementById('voice-select');
    const voiceDesc = document.getElementById('voice-desc');
    const speedRange = document.getElementById('speed-range');
    const speedDisplay = document.getElementById('speed-display');
    const speedPresets = document.querySelectorAll('.btn-preset');
    const scriptText = document.getElementById('script-text');
    const charCounter = document.getElementById('char-counter');
    const btnInsertPause = document.getElementById('btn-insert-pause');
    const btnSampleText = document.getElementById('btn-sample-text');
    const btnClearText = document.getElementById('btn-clear-text');
    const btnGenerate = document.getElementById('btn-generate');
    const generationStatus = document.getElementById('generation-status');
    const audioCard = document.getElementById('audio-output-card');
    const audioPlayer = document.getElementById('audio-player');
    const btnDownloadAudio = document.getElementById('btn-download-audio');
    const audioTitle = document.getElementById('audio-title');
    const audioMeta = document.getElementById('audio-meta');
    const gpuBadge = document.getElementById('gpu-badge');

    const SAMPLES = {
        es: "Buenos días a todos. En esta lección aprenderemos los conceptos fundamentales de la investigación científica. [pausa] Es indispensable estructurar una pregunta clara y valorar rigurosamente la evidencia metodológica.",
        en: "Welcome to this educational session. Today, we will explore the fundamental principles of artificial intelligence and science. [pausa] Please follow each step carefully before starting the interactive exercises."
    };

    // 1. Inicialización
    async function init() {
        // Cargar estado y GPU
        loadServerStatus();

        // Cargar voces del catálogo
        try {
            const res = await fetch('/api/voices');
            if (res.ok) {
                catalog = await res.json();
                renderVoiceOptions();
            } else {
                showStatus('Error al cargar catálogo de voces', 'error');
            }
        } catch (err) {
            console.error(err);
            showStatus('No se pudo conectar con el servidor', 'error');
        }

        // Cargar texto de ejemplo inicial
        scriptText.value = SAMPLES.es;
        updateTextStats();
    }

    async function loadServerStatus() {
        try {
            const res = await fetch('/api/status');
            if (res.ok) {
                const data = await res.json();
                if (data.gpu_available && gpuBadge) {
                    gpuBadge.innerHTML = `<i class="fa-solid fa-microchip"></i> <span>Kokoro (${data.device})</span>`;
                    gpuBadge.title = `Aceleración GPU activa: ${data.device}`;
                }
            }
        } catch (e) {
            console.warn("Status check failed:", e);
        }
    }

    // 2. Renderizar Opciones de Voz
    function renderVoiceOptions() {
        voiceSelect.innerHTML = '';
        const voices = catalog[currentLang] || [];

        if (voices.length === 0) {
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = 'No hay voces disponibles';
            voiceSelect.appendChild(opt);
            voiceDesc.textContent = '';
            return;
        }

        voices.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v.id;
            const star = v.recommended ? ' ⭐' : '';
            opt.textContent = `${v.name} (${v.gender} • ${v.accent})${star}`;
            voiceSelect.appendChild(opt);
        });

        // Seleccionar la primera recomendada
        const firstRec = voices.find(v => v.recommended) || voices[0];
        voiceSelect.value = firstRec.id;
        updateVoiceDescription();
    }

    function updateVoiceDescription() {
        const voices = catalog[currentLang] || [];
        const selected = voices.find(v => v.id === voiceSelect.value);
        if (selected) {
            const engineLabel = selected.engine === 'kokoro' ? 'Motor Kokoro-82M (GPU)' : 'Motor Edge Neural (Estudio)';
            voiceDesc.innerHTML = `<strong>${selected.name}:</strong> ${selected.description} <br><small class="engine-tag">${engineLabel}</small>`;
        } else {
            voiceDesc.textContent = '';
        }
    }

    // 3. Control de Velocidad Pedagógica
    function setSpeed(val) {
        currentSpeed = parseFloat(val);
        speedRange.value = currentSpeed;
        
        let label = `${currentSpeed.toFixed(2)}x`;
        if (currentSpeed === 0.95) label += ' (Recomendado Docente)';
        else if (currentSpeed === 0.90) label += ' (Pausado / Explicativo)';
        else if (currentSpeed === 1.00) label += ' (Normal)';
        else if (currentSpeed === 1.10) label += ' (Dinámico)';
        
        speedDisplay.textContent = label;

        // Actualizar botón preset activo
        speedPresets.forEach(btn => {
            btn.classList.toggle('active', parseFloat(btn.dataset.speed) === currentSpeed);
        });

        updateTextStats();
    }

    // 4. Estadísticas del Texto (Palabras, Caracteres, Duración Estimada)
    function updateTextStats() {
        const text = scriptText.value.trim();
        const chars = text.length;
        const words = text ? text.split(/\s+/).length : 0;

        // Estimación: ~140 palabras por minuto a 1.0x para material docente
        const wordsPerSec = (140 * currentSpeed) / 60;
        const estSeconds = words > 0 ? Math.ceil(words / wordsPerSec) : 0;

        charCounter.textContent = `${chars} caracteres | ${words} palabras | ~${estSeconds}s estimadas`;
    }

    // 5. Generar Narración
    async function handleGenerate() {
        const text = scriptText.value.trim();
        if (!text) {
            showStatus('Por favor, escribe un guion antes de generar.', 'warning');
            scriptText.focus();
            return;
        }

        const voiceId = voiceSelect.value;
        if (!voiceId) {
            showStatus('Selecciona una voz para continuar.', 'warning');
            return;
        }

        // UI Loading
        btnGenerate.disabled = true;
        btnGenerate.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Sintetizando lección...</span>`;
        showStatus('Procesando audio de alta fidelidad...', 'loading');

        const startTime = Date.now();

        try {
            const payload = {
                text: text,
                voice: voiceId,
                language: currentLang,
                speed: currentSpeed
            };

            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                let errMsg = 'Error al generar el audio';
                try {
                    const errData = await response.json();
                    errMsg = errData.detail || errMsg;
                } catch (e) {}
                throw new Error(errMsg);
            }

            const audioBlob = await response.blob();
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

            // Liberar URL previa si existía
            if (currentAudioUrl) {
                URL.revokeObjectURL(currentAudioUrl);
            }

            currentAudioUrl = URL.createObjectURL(audioBlob);

            // Mostrar reproductor
            audioPlayer.src = currentAudioUrl;
            audioPlayer.load();
            audioPlayer.play().catch(() => {}); // Autoplay si el navegador lo permite

            const voices = catalog[currentLang] || [];
            const selectedVoice = voices.find(v => v.id === voiceId);
            const voiceName = selectedVoice ? selectedVoice.name : voiceId;

            audioTitle.textContent = `Narración: ${voiceName}`;
            const sizeKb = (audioBlob.size / 1024).toFixed(0);
            audioMeta.textContent = `WAV PCM • ${sizeKb} KB • Generado en ${elapsed}s (${currentSpeed}x)`;

            // Configurar botón de descarga
            const dateStr = new Date().toISOString().slice(0, 10);
            btnDownloadAudio.href = currentAudioUrl;
            btnDownloadAudio.download = `${voiceId}_${dateStr}.wav`;

            audioCard.style.display = 'block';
            audioCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

            showStatus(`¡Audio generado con éxito en ${elapsed}s!`, 'success');

        } catch (error) {
            console.error(error);
            showStatus(`Error: ${error.message}`, 'error');
        } finally {
            btnGenerate.disabled = false;
            btnGenerate.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Generar Narración</span>`;
        }
    }

    function showStatus(msg, type) {
        generationStatus.className = `generation-status status-${type}`;
        let icon = '';
        if (type === 'loading') icon = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
        else if (type === 'success') icon = '<i class="fa-solid fa-check"></i>';
        else if (type === 'error') icon = '<i class="fa-solid fa-triangle-exclamation"></i>';
        else if (type === 'warning') icon = '<i class="fa-solid fa-circle-exclamation"></i>';

        generationStatus.innerHTML = `${icon} <span>${msg}</span>`;
    }

    // 6. Event Listeners
    langTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const newLang = tab.dataset.lang;
            if (newLang === currentLang) return;

            langTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            currentLang = newLang;
            renderVoiceOptions();

            // Si el texto coincide con el ejemplo anterior o está vacío, poner el nuevo ejemplo
            if (!scriptText.value.trim() || scriptText.value.trim() === SAMPLES.es || scriptText.value.trim() === SAMPLES.en) {
                scriptText.value = SAMPLES[currentLang];
                updateTextStats();
            }
        });
    });

    voiceSelect.addEventListener('change', updateVoiceDescription);

    speedRange.addEventListener('input', (e) => setSpeed(e.target.value));

    speedPresets.forEach(btn => {
        btn.addEventListener('click', () => setSpeed(btn.dataset.speed));
    });

    scriptText.addEventListener('input', updateTextStats);

    btnInsertPause.addEventListener('click', () => {
        const start = scriptText.selectionStart;
        const end = scriptText.selectionEnd;
        const val = scriptText.value;
        const pauseTag = ' [pausa] ';
        scriptText.value = val.substring(0, start) + pauseTag + val.substring(end);
        scriptText.selectionStart = scriptText.selectionEnd = start + pauseTag.length;
        scriptText.focus();
        updateTextStats();
    });

    btnSampleText.addEventListener('click', () => {
        scriptText.value = SAMPLES[currentLang];
        updateTextStats();
    });

    btnClearText.addEventListener('click', () => {
        scriptText.value = '';
        updateTextStats();
        scriptText.focus();
    });

    btnGenerate.addEventListener('click', handleGenerate);

    // Permitir Ctrl+Enter para generar rápidamente
    scriptText.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            handleGenerate();
        }
    });

    // Iniciar aplicación
    init();
});
