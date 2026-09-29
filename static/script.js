// Voice-TTS Studio - Educational Narration Client

document.addEventListener('DOMContentLoaded', () => {
    // State
    let catalog = { es: [], en: [] };
    let currentLang = 'es';
    let currentSpeed = 0.95;
    let currentFormat = 'mp3';
    let currentAudioUrl = null;
    let currentInputMode = 'text'; // 'text' o 'subtitle'
    let currentSubMode = 'synced';  // 'synced' o 'continuous'

    // DOM Elements - Studio Base
    const langTabs = document.querySelectorAll('.lang-tab');
    const voiceSelect = document.getElementById('voice-select');
    const voiceDesc = document.getElementById('voice-desc');
    const speedRange = document.getElementById('speed-range');
    const speedDisplay = document.getElementById('speed-display');
    const speedPresets = document.querySelectorAll('.btn-preset');
    const formatButtons = document.querySelectorAll('.btn-format');
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
    const downloadExt = document.getElementById('download-ext');
    const audioTitle = document.getElementById('audio-title');
    const audioMeta = document.getElementById('audio-meta');
    const gpuBadge = document.getElementById('gpu-badge');
    const mimoBadge = document.getElementById('mimo-badge');
    const directorModeContainer = document.getElementById('director-mode-container');
    const stylePromptInput = document.getElementById('style-prompt-input');
    const btnTagLaughter = document.getElementById('btn-tag-laughter');
    const btnTagSigh = document.getElementById('btn-tag-sigh');
    const btnTagWhisper = document.getElementById('btn-tag-whisper');
    const directorPresets = document.querySelectorAll('.btn-director-preset');

    // DOM Elements - Subtitle Mode
    const tabModeText = document.getElementById('tab-mode-text');
    const tabModeSubtitle = document.getElementById('tab-mode-subtitle');
    const textEditorContainer = document.getElementById('text-editor-container');
    const subtitleEditorContainer = document.getElementById('subtitle-editor-container');
    const subtitleDropzone = document.getElementById('subtitle-dropzone');
    const btnBrowseSubtitle = document.getElementById('btn-browse-subtitle');
    const subtitleFileInput = document.getElementById('subtitle-file-input');
    const subtitleText = document.getElementById('subtitle-text');
    const subtitleCounter = document.getElementById('subtitle-counter');
    const btnSampleSubtitle = document.getElementById('btn-sample-subtitle');
    const btnClearSubtitle = document.getElementById('btn-clear-subtitle');
    const btnSubModes = document.querySelectorAll('.btn-sub-mode');

    const SAMPLES = {
        es: "Buenos días a todos. En esta lección aprenderemos los conceptos fundamentales de la investigación científica. [pausa] Es indispensable estructurar una pregunta clara y valorar rigurosamente la evidencia metodológica.",
        en: "Welcome to this educational session. Today, we will explore the fundamental principles of artificial intelligence and science. [pausa] Please follow each step carefully before starting the interactive exercises."
    };

    const SUBTITLE_SAMPLES = {
        es: `1\n00:00:00,500 --> 00:00:03,500\nBienvenidos a esta lección interactiva sobre inteligencia artificial.\n\n2\n00:00:04,200 --> 00:00:07,800\nHoy aprenderemos cómo convertir subtítulos en una pista de voz sincronizada.\n\n3\n00:00:08,500 --> 00:00:11,500\n¡El audio respetará cada segundo y marca de tiempo del video!`,
        en: `1\n00:00:00.500 --> 00:00:03.500\nWelcome to this educational video on modern artificial intelligence.\n\n2\n00:00:04.200 --> 00:00:07.800\nToday we will demonstrate real-time subtitle-to-speech synchronization.\n\n3\n00:00:08.500 --> 00:00:11.500\nEvery segment aligns perfectly with the video timestamps!`
    };

    // 1. Inicialización
    async function init() {
        // Cargar estado y GPU / MiMo
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
                if (mimoBadge && data.engines && data.engines.mimo) {
                    const isMimoOk = !data.engines.mimo.includes('Inactivo');
                    mimoBadge.style.opacity = isMimoOk ? '1' : '0.5';
                    mimoBadge.title = isMimoOk ? 'Xiaomi MiMo v2.5 Cloud Activo' : 'MIMO_API_KEY no configurada';
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

        // Agrupar por categoría
        const categories = {};
        voices.forEach(v => {
            const cat = v.category || (v.engine === 'kokoro' ? 'Kokoro AI (Inglés)' : 'Microsoft Edge (Español)');
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push(v);
        });

        Object.keys(categories).forEach(cat => {
            const group = document.createElement('optgroup');
            group.label = cat;
            categories[cat].forEach(v => {
                const opt = document.createElement('option');
                opt.value = v.id;
                const star = v.recommended ? ' ⭐' : '';
                opt.textContent = `${v.name} (${v.gender} • ${v.accent})${star}`;
                group.appendChild(opt);
            });
            voiceSelect.appendChild(group);
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
            let engineLabel = 'Motor Edge Neural (Estudio)';
            const isMimo = selected.engine === 'mimo' || (selected.id && selected.id.startsWith('mimo-'));
            if (selected.engine === 'kokoro') {
                engineLabel = 'Motor Kokoro-82M (GPU)';
            } else if (isMimo) {
                engineLabel = 'Motor Xiaomi MiMo v2.5 (Cloud • Modo Director & Audio Tags)';
            }

            voiceDesc.innerHTML = `<strong>${selected.name}:</strong> ${selected.description} <br><small class="engine-tag">${engineLabel}</small>`;

            // Mostrar u ocultar panel de Modo Director y botones de tags de MiMo
            if (directorModeContainer) {
                directorModeContainer.style.display = isMimo ? 'block' : 'none';
            }
            if (btnTagLaughter) btnTagLaughter.style.display = isMimo ? 'inline-flex' : 'none';
            if (btnTagSigh) btnTagSigh.style.display = isMimo ? 'inline-flex' : 'none';
            if (btnTagWhisper) btnTagWhisper.style.display = isMimo ? 'inline-flex' : 'none';
        } else {
            voiceDesc.textContent = '';
            if (directorModeContainer) directorModeContainer.style.display = 'none';
            if (btnTagLaughter) btnTagLaughter.style.display = 'none';
            if (btnTagSigh) btnTagSigh.style.display = 'none';
            if (btnTagWhisper) btnTagWhisper.style.display = 'none';
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

    // 4.1. Estadísticas de Subtítulos (.SRT / .VTT)
    function updateSubtitleStats() {
        if (!subtitleText || !subtitleCounter) return;
        const content = subtitleText.value.trim();
        if (!content) {
            subtitleCounter.textContent = '0 subtítulos detectados | ~0s de duración total';
            return;
        }

        // Buscar marcas de tiempo 00:00:00,000 --> 00:00:00,000
        const timePat = /(?:(?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{3}))\s*-->\s*(?:(?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{3}))/g;
        let count = 0;
        let lastEndSec = 0;
        let m;

        while ((m = timePat.exec(content)) !== null) {
            count++;
            const h2 = m[5] ? parseInt(m[5], 10) : 0;
            const m2 = parseInt(m[6], 10);
            const s2 = parseInt(m[7], 10);
            const endSec = h2 * 3600 + m2 * 60 + s2;
            if (endSec > lastEndSec) lastEndSec = endSec;
        }

        if (count > 0) {
            const mins = Math.floor(lastEndSec / 60);
            const secs = lastEndSec % 60;
            const timeStr = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
            subtitleCounter.textContent = `${count} subtítulos detectados | ~${timeStr} de duración total de video`;
        } else {
            subtitleCounter.textContent = 'No se detectaron marcas de tiempo válidas (formato 00:00:01,000 --> 00:00:04,000)';
        }
    }

    function handleSubtitleFile(file) {
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            subtitleText.value = e.target.result;
            updateSubtitleStats();
            showStatus(`Archivo "${file.name}" cargado correctamente`, 'success');
        };
        reader.onerror = () => {
            showStatus('Error al leer el archivo de subtítulos', 'error');
        };
        reader.readAsText(file);
    }

    // 5. Generar Narración o Doblaje de Subtítulos
    async function handleGenerate() {
        const voiceId = voiceSelect.value;
        if (!voiceId) {
            showStatus('Selecciona una voz para continuar.', 'warning');
            return;
        }

        const startTime = Date.now();
        const isSubtitle = (currentInputMode === 'subtitle');

        if (isSubtitle) {
            const subContent = subtitleText.value.trim();
            if (!subContent) {
                showStatus('Por favor, ingresa o arrastra un archivo de subtítulos antes de generar.', 'warning');
                subtitleText.focus();
                return;
            }

            btnGenerate.disabled = true;
            btnGenerate.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Alineando subtítulos y voz...</span>`;
            const modeDesc = (currentSubMode === 'synced') ? 'doblaje sincronizado con marcas de tiempo' : 'narración continua';
            showStatus(`Procesando ${modeDesc}... (esto puede tardar unos segundos)`, 'loading');

            try {
                const payload = {
                    subtitle_text: subContent,
                    voice: voiceId,
                    language: currentLang,
                    speed: currentSpeed,
                    mode: currentSubMode,
                    format: currentFormat
                };

                if (stylePromptInput && stylePromptInput.value.trim()) {
                    payload.style_prompt = stylePromptInput.value.trim();
                }

                const response = await fetch('/api/tts/subtitle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    let errMsg = 'Error al procesar subtítulos';
                    try {
                        const errData = await response.json();
                        errMsg = errData.detail || errMsg;
                    } catch (e) {}
                    throw new Error(errMsg);
                }

                const subCountHeader = response.headers.get('X-Subtitle-Count');
                const audioBlob = await response.blob();
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

                if (currentAudioUrl) URL.revokeObjectURL(currentAudioUrl);
                currentAudioUrl = URL.createObjectURL(audioBlob);

                audioPlayer.src = currentAudioUrl;
                audioPlayer.load();
                audioPlayer.play().catch(() => {});

                const voices = catalog[currentLang] || [];
                const selectedVoice = voices.find(v => v.id === voiceId);
                const voiceName = selectedVoice ? selectedVoice.name : voiceId;

                const subModeLabel = (currentSubMode === 'synced') ? 'Doblaje Sincronizado' : 'Audiolibro Corrido';
                audioTitle.textContent = `${subModeLabel}: ${voiceName}`;
                const sizeKb = (audioBlob.size / 1024).toFixed(0);
                const fmtUpper = currentFormat.toUpperCase();
                const countStr = subCountHeader ? `${subCountHeader} frases • ` : '';
                audioMeta.textContent = `${fmtUpper} • ${sizeKb} KB • ${countStr}Generado en ${elapsed}s`;

                const dateStr = new Date().toISOString().slice(0, 10);
                btnDownloadAudio.href = currentAudioUrl;
                btnDownloadAudio.download = `subtitles_${currentSubMode}_${voiceId}_${dateStr}.${currentFormat}`;
                if (downloadExt) downloadExt.textContent = fmtUpper;

                audioCard.style.display = 'block';
                audioCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

                showStatus(`¡Audio de subtítulos generado con éxito en ${elapsed}s!`, 'success');

            } catch (error) {
                console.error(error);
                showStatus(`Error: ${error.message}`, 'error');
            } finally {
                btnGenerate.disabled = false;
                btnGenerate.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Generar Narración</span>`;
            }
            return;
        }

        // Modo Convencional (Texto Libre)
        const text = scriptText.value.trim();
        if (!text) {
            showStatus('Por favor, escribe un guion antes de generar.', 'warning');
            scriptText.focus();
            return;
        }

        // UI Loading
        btnGenerate.disabled = true;
        btnGenerate.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Sintetizando lección...</span>`;
        showStatus('Procesando audio de alta fidelidad...', 'loading');

        try {
            const payload = {
                text: text,
                voice: voiceId,
                language: currentLang,
                speed: currentSpeed,
                format: currentFormat
            };

            if (stylePromptInput && stylePromptInput.value.trim()) {
                payload.style_prompt = stylePromptInput.value.trim();
            }

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
            const fmtUpper = currentFormat.toUpperCase();
            audioMeta.textContent = `${fmtUpper} • ${sizeKb} KB • Generado en ${elapsed}s (${currentSpeed}x)`;

            // Configurar botón de descarga
            const dateStr = new Date().toISOString().slice(0, 10);
            btnDownloadAudio.href = currentAudioUrl;
            btnDownloadAudio.download = `${voiceId}_${dateStr}.${currentFormat}`;
            if (downloadExt) downloadExt.textContent = fmtUpper;

            audioCard.style.display = 'block';
            audioCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

            showStatus(`¡Audio ${fmtUpper} generado con éxito en ${elapsed}s!`, 'success');

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

            // Actualizar muestra de subtítulos si está vacía
            if (!subtitleText.value.trim() || subtitleText.value.trim() === SUBTITLE_SAMPLES.es || subtitleText.value.trim() === SUBTITLE_SAMPLES.en) {
                subtitleText.value = SUBTITLE_SAMPLES[currentLang];
                updateSubtitleStats();
            }
        });
    });

    // Control de Modo de Entrada (Texto vs Subtítulos)
    if (tabModeText && tabModeSubtitle) {
        tabModeText.addEventListener('click', () => {
            tabModeText.classList.add('active');
            tabModeSubtitle.classList.remove('active');
            textEditorContainer.style.display = 'block';
            subtitleEditorContainer.style.display = 'none';
            currentInputMode = 'text';
            btnGenerate.querySelector('span').textContent = 'Generar Narración';
        });

        tabModeSubtitle.addEventListener('click', () => {
            tabModeSubtitle.classList.add('active');
            tabModeText.classList.remove('active');
            textEditorContainer.style.display = 'none';
            subtitleEditorContainer.style.display = 'block';
            currentInputMode = 'subtitle';
            btnGenerate.querySelector('span').textContent = 'Generar Audio de Subtítulos';

            if (!subtitleText.value.trim()) {
                subtitleText.value = SUBTITLE_SAMPLES[currentLang];
                updateSubtitleStats();
            }
        });
    }

    // Control de Modo de Subtítulos (Sincronizado vs Continuo)
    btnSubModes.forEach(btn => {
        btn.addEventListener('click', () => {
            btnSubModes.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentSubMode = btn.dataset.submode || 'synced';
        });
    });

    // Dropzone de Subtítulos
    if (subtitleDropzone && subtitleFileInput) {
        subtitleDropzone.addEventListener('click', (e) => {
            if (e.target.id === 'btn-browse-subtitle' || e.target.closest('#btn-browse-subtitle')) {
                subtitleFileInput.click();
            } else if (e.target === subtitleDropzone || e.target.closest('.dropzone-icon') || e.target.closest('.dropzone-text')) {
                subtitleFileInput.click();
            }
        });

        subtitleDropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            subtitleDropzone.classList.add('dragover');
        });

        subtitleDropzone.addEventListener('dragleave', () => {
            subtitleDropzone.classList.remove('dragover');
        });

        subtitleDropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            subtitleDropzone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                handleSubtitleFile(files[0]);
            }
        });

        subtitleFileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                handleSubtitleFile(e.target.files[0]);
            }
        });
    }

    if (btnSampleSubtitle) {
        btnSampleSubtitle.addEventListener('click', () => {
            subtitleText.value = SUBTITLE_SAMPLES[currentLang];
            updateSubtitleStats();
        });
    }

    if (btnClearSubtitle) {
        btnClearSubtitle.addEventListener('click', () => {
            subtitleText.value = '';
            updateSubtitleStats();
            subtitleText.focus();
        });
    }

    if (subtitleText) {
        subtitleText.addEventListener('input', updateSubtitleStats);
    }

    voiceSelect.addEventListener('change', updateVoiceDescription);

    speedRange.addEventListener('input', (e) => setSpeed(e.target.value));

    speedPresets.forEach(btn => {
        btn.addEventListener('click', () => setSpeed(btn.dataset.speed));
    });

    formatButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            formatButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFormat = btn.dataset.format;
            if (downloadExt) downloadExt.textContent = currentFormat.toUpperCase();
        });
    });

    scriptText.addEventListener('input', updateTextStats);

    function insertTagAtCursor(tag) {
        const start = scriptText.selectionStart;
        const end = scriptText.selectionEnd;
        const val = scriptText.value;
        const paddedTag = ` ${tag} `;
        scriptText.value = val.substring(0, start) + paddedTag + val.substring(end);
        scriptText.selectionStart = scriptText.selectionEnd = start + paddedTag.length;
        scriptText.focus();
        updateTextStats();
    }

    btnInsertPause.addEventListener('click', () => insertTagAtCursor('[pausa]'));

    if (btnTagLaughter) {
        btnTagLaughter.addEventListener('click', () => insertTagAtCursor('[laughter]'));
    }
    if (btnTagSigh) {
        btnTagSigh.addEventListener('click', () => insertTagAtCursor('[sigh]'));
    }
    if (btnTagWhisper) {
        btnTagWhisper.addEventListener('click', () => insertTagAtCursor('[whisper]'));
    }

    directorPresets.forEach(btn => {
        btn.addEventListener('click', () => {
            if (stylePromptInput) {
                stylePromptInput.value = btn.dataset.style;
                stylePromptInput.focus();
            }
        });
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
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            handleGenerate();
        }
    });

    // Iniciar aplicación
    init();
});
