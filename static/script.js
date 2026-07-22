document.addEventListener('DOMContentLoaded', () => {
    const API = '';

    // --- DOM ---
    const statusBadge   = document.getElementById('tts-status');
    const btnStart      = document.getElementById('btn-start');
    const btnStop       = document.getElementById('btn-stop');
    const btnRefresh    = document.getElementById('btn-refresh');
    const serverLog     = document.getElementById('server-log');
    const btnRefreshLog = document.getElementById('btn-refresh-log');

    const dropzone        = document.getElementById('dropzone');
    const fileInput       = document.getElementById('speaker-file-input');
    const uploadStatus    = document.getElementById('upload-status');
    const voiceList       = document.getElementById('voice-list');

    const testSpeaker  = document.getElementById('test-speaker');
    const testLang     = document.getElementById('test-lang');
    const testText     = document.getElementById('test-text');
    const btnTest      = document.getElementById('btn-test');
    const testStatus   = document.getElementById('test-status');
    const testAudioCtn = document.getElementById('test-audio-container');
    const testAudio    = document.getElementById('test-audio');

    const btnCopyUrl   = document.getElementById('btn-copy-url');
    const apiSpeakerName = document.getElementById('api-speaker-name');

    // Advanced Parameters DOM
    const testTemp         = document.getElementById('test-temp');
    const valTemp          = document.getElementById('val-temp');
    const testLengthPenalty = document.getElementById('test-length-penalty');
    const valLenPenalty    = document.getElementById('val-len-penalty');
    const testRepPenalty   = document.getElementById('test-rep-penalty');
    const valRepPenalty    = document.getElementById('val-rep-penalty');
    const testTopK         = document.getElementById('test-top-k');
    const valTopK          = document.getElementById('val-top-k');
    const testTopP         = document.getElementById('test-top-p');
    const valTopP          = document.getElementById('val-top-p');
    const testRemoveCeceo  = document.getElementById('test-remove-ceceo');

    // Update label values on slider movement
    testTemp.addEventListener('input', () => valTemp.textContent = testTemp.value);
    testLengthPenalty.addEventListener('input', () => valLenPenalty.textContent = testLengthPenalty.value);
    testRepPenalty.addEventListener('input', () => valRepPenalty.textContent = testRepPenalty.value);
    testTopK.addEventListener('input', () => valTopK.textContent = testTopK.value);
    testTopP.addEventListener('input', () => valTopP.textContent = testTopP.value);

    let currentPlayingAudio = null;

    // =========================================================================
    //  Server Control
    // =========================================================================

    async function checkStatus() {
        try {
            const res = await fetch(`${API}/api/status`);
            const data = await res.json();
            setStatus(data.status === 'connected');
        } catch {
            setStatus(false);
        }
    }

    function setStatus(connected) {
        if (connected) {
            statusBadge.className = 'status-badge status-connected';
            statusBadge.querySelector('.status-text').textContent = 'Conectado';
            btnStart.disabled = true;
            btnStop.disabled = false;
        } else {
            statusBadge.className = 'status-badge status-disconnected';
            statusBadge.querySelector('.status-text').textContent = 'Apagado';
            btnStart.disabled = false;
            btnStop.disabled = false;
        }
    }

    function setStatusLoading(text) {
        statusBadge.className = 'status-badge status-loading';
        statusBadge.querySelector('.status-text').textContent = text;
        btnStart.disabled = true;
        btnStop.disabled = true;
    }

    btnStart.addEventListener('click', async () => {
        setStatusLoading('Iniciando...');
        try {
            const res = await fetch(`${API}/api/server/start`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                // Poll until server is ready (up to 90s)
                setStatusLoading('Cargando modelo...');
                pollUntilReady(90);
            } else {
                alert('Error: ' + data.error);
                checkStatus();
            }
        } catch (e) {
            alert('Error de conexion: ' + e.message);
            checkStatus();
        }
    });

    btnStop.addEventListener('click', async () => {
        setStatusLoading('Apagando...');
        try {
            await fetch(`${API}/api/server/stop`, { method: 'POST' });
        } catch { /* ignore */ }
        // Wait a moment then recheck
        setTimeout(checkStatus, 1500);
    });

    btnRefresh.addEventListener('click', () => {
        btnRefresh.querySelector('i').classList.add('fa-spin');
        checkStatus().then(() => loadSpeakers()).finally(() => {
            setTimeout(() => btnRefresh.querySelector('i').classList.remove('fa-spin'), 400);
        });
    });

    function pollUntilReady(maxSeconds) {
        let elapsed = 0;
        const interval = setInterval(async () => {
            elapsed += 3;
            if (elapsed > maxSeconds) {
                clearInterval(interval);
                setStatus(false);
                alert('El servidor tardo demasiado en iniciar. Revisa el log para ver errores.');
                return;
            }
            try {
                const res = await fetch(`${API}/api/status`);
                const data = await res.json();
                if (data.status === 'connected') {
                    clearInterval(interval);
                    setStatus(true);
                    loadSpeakers();
                }
            } catch { /* keep trying */ }
        }, 3000);
    }

    // Log viewer
    btnRefreshLog.addEventListener('click', loadLog);
    async function loadLog() {
        try {
            const res = await fetch(`${API}/api/server/log?lines=60`);
            const data = await res.json();
            serverLog.textContent = data.log || 'Sin datos de log...';
            serverLog.scrollTop = serverLog.scrollHeight;
        } catch {
            serverLog.textContent = 'Error al cargar el log.';
        }
    }

    // =========================================================================
    //  Voice Management
    // =========================================================================

    async function loadSpeakers() {
        try {
            const res = await fetch(`${API}/api/speakers`);
            const data = await res.json();
            renderVoiceList(data.speakers || []);
            populateTestSpeaker(data.speakers || []);
        } catch {
            voiceList.innerHTML = '<div class="voice-list-empty"><i class="fa-solid fa-triangle-exclamation"></i><span>Error al cargar voces</span></div>';
        }
    }

    function renderVoiceList(speakers) {
        if (speakers.length === 0) {
            voiceList.innerHTML = '<div class="voice-list-empty"><i class="fa-solid fa-volume-xmark"></i><span>No hay voces cargadas</span></div>';
            return;
        }
        voiceList.innerHTML = '';
        speakers.forEach(s => {
            const item = document.createElement('div');
            item.className = 'voice-item';
            item.innerHTML = `
                <div class="voice-item-icon"><i class="fa-solid fa-waveform-lines"></i></div>
                <div class="voice-item-info">
                    <div class="voice-item-name">${s.name}</div>
                    <div class="voice-item-size">${s.size_kb} KB</div>
                </div>
                <div class="voice-item-actions">
                    <button class="btn-play-voice" title="Escuchar"><i class="fa-solid fa-play"></i></button>
                    <button class="btn-delete-voice" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
                </div>
            `;
            // Play button
            const btnPlay = item.querySelector('.btn-play-voice');
            btnPlay.addEventListener('click', () => playVoice(s.name, btnPlay));
            // Delete button
            item.querySelector('.btn-delete-voice').addEventListener('click', () => deleteVoice(s.name));
            voiceList.appendChild(item);
        });
    }

    function populateTestSpeaker(speakers) {
        const current = testSpeaker.value;
        testSpeaker.innerHTML = '<option value="">-- selecciona --</option>';
        speakers.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.name;
            opt.textContent = s.name;
            testSpeaker.appendChild(opt);
        });
        if (current && speakers.find(s => s.name === current)) {
            testSpeaker.value = current;
        } else if (speakers.length > 0) {
            testSpeaker.value = speakers[0].name;
        }
        // Update API doc example
        if (testSpeaker.value) {
            apiSpeakerName.textContent = testSpeaker.value;
        }
    }

    testSpeaker.addEventListener('change', () => {
        if (testSpeaker.value) apiSpeakerName.textContent = testSpeaker.value;
    });

    function playVoice(name, btnEl) {
        // Stop any currently playing audio
        if (currentPlayingAudio) {
            currentPlayingAudio.pause();
            currentPlayingAudio = null;
            document.querySelectorAll('.btn-play-voice').forEach(b => b.innerHTML = '<i class="fa-solid fa-play"></i>');
        }
        const audio = new Audio(`${API}/api/speakers/${encodeURIComponent(name)}/audio`);
        audio.play();
        currentPlayingAudio = audio;
        btnEl.innerHTML = '<i class="fa-solid fa-pause"></i>';
        audio.addEventListener('ended', () => {
            btnEl.innerHTML = '<i class="fa-solid fa-play"></i>';
            currentPlayingAudio = null;
        });
    }

    async function deleteVoice(name) {
        if (!confirm(`Eliminar la voz "${name}"?`)) return;
        try {
            await fetch(`${API}/api/speakers/${encodeURIComponent(name)}`, { method: 'DELETE' });
            loadSpeakers();
        } catch { alert('Error al eliminar.'); }
    }

    // Upload
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', e => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files);
    });
    fileInput.addEventListener('change', () => { if (fileInput.files.length) uploadFiles(fileInput.files); });

    async function uploadFiles(files) {
        for (const file of files) {
            if (!file.name.toLowerCase().endsWith('.wav')) {
                uploadStatus.style.color = 'var(--error)';
                uploadStatus.textContent = `"${file.name}" no es .wav, ignorado.`;
                continue;
            }
            uploadStatus.style.color = 'var(--text-secondary)';
            uploadStatus.textContent = `Subiendo ${file.name}...`;
            const fd = new FormData();
            fd.append('file', file);
            try {
                const res = await fetch(`${API}/api/speakers/upload`, { method: 'POST', body: fd });
                const data = await res.json();
                if (data.success) {
                    uploadStatus.style.color = 'var(--success)';
                    uploadStatus.textContent = `"${data.filename}" subido (${data.size_kb} KB)`;
                } else {
                    uploadStatus.style.color = 'var(--error)';
                    uploadStatus.textContent = 'Error: ' + data.error;
                }
            } catch {
                uploadStatus.style.color = 'var(--error)';
                uploadStatus.textContent = 'Error de conexion al subir.';
            }
        }
        loadSpeakers();
        fileInput.value = '';
    }

    // =========================================================================
    //  Quick Test
    // =========================================================================

    btnTest.addEventListener('click', async () => {
        const speaker = testSpeaker.value;
        const lang = testLang.value;
        const text = testText.value.trim();

        if (!speaker) { alert('Selecciona una voz de referencia.'); return; }
        if (!text) { alert('Escribe un texto de prueba.'); return; }

        btnTest.disabled = true;
        testStatus.textContent = 'Generando audio...';
        testStatus.style.color = 'var(--text-secondary)';
        testAudioCtn.style.display = 'none';

        const startTime = Date.now();

        try {
            const temperature = parseFloat(testTemp.value);
            const length_penalty = parseFloat(testLengthPenalty.value);
            const repetition_penalty = parseFloat(testRepPenalty.value);
            const top_k = parseInt(testTopK.value, 10);
            const top_p = parseFloat(testTopP.value);
            const remove_ceceo = testRemoveCeceo.checked;

            const res = await fetch(`${API}/api/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text,
                    speaker_wav: speaker,
                    language: lang,
                    temperature,
                    length_penalty,
                    repetition_penalty,
                    top_k,
                    top_p,
                    remove_ceceo
                }),
            });

            if (!res.ok) {
                let errMsg;
                try { errMsg = (await res.json()).detail; } catch { errMsg = res.statusText; }
                testStatus.style.color = 'var(--error)';
                testStatus.textContent = 'Error: ' + errMsg;
                btnTest.disabled = false;
                return;
            }

            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            testAudio.src = url;
            testAudioCtn.style.display = 'block';
            testAudio.play();

            const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
            testStatus.style.color = 'var(--success)';
            testStatus.textContent = `Listo (${elapsed}s)`;
        } catch (e) {
            testStatus.style.color = 'var(--error)';
            testStatus.textContent = 'Error: ' + e.message;
        }
        btnTest.disabled = false;
    });

    // Copy URL
    btnCopyUrl.addEventListener('click', () => {
        const url = document.getElementById('api-url').textContent;
        navigator.clipboard.writeText(url).then(() => {
            btnCopyUrl.innerHTML = '<i class="fa-solid fa-check"></i>';
            setTimeout(() => { btnCopyUrl.innerHTML = '<i class="fa-solid fa-copy"></i>'; }, 1500);
        });
    });

    // =========================================================================
    //  Init
    // =========================================================================
    checkStatus();
    loadSpeakers();
    setInterval(checkStatus, 10000);
});
