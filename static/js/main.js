document.addEventListener('DOMContentLoaded', () => {
    // ===================== DOM REFS =====================
    const sentenceDisplay   = document.getElementById('sentence-display');
    const btnSpeak          = document.getElementById('btn-speak');
    const btnClearChar      = document.getElementById('btn-clear-char');
    const btnClear          = document.getElementById('btn-clear');
    const btnToggleCapture  = document.getElementById('btn-toggle-capture');
    const progressRing      = document.getElementById('progress-ring');
    const charCenter        = document.getElementById('char-center');
    const statusChar        = document.getElementById('status-char');
    const statusState       = document.getElementById('status-state');
    const confirmToast      = document.getElementById('confirm-toast');
    const toastChar         = document.getElementById('toast-char');
    const twoHandBadge      = document.getElementById('two-hand-badge');

    // ===================== STATE =====================
    let isCapturing         = true;
    let lastSentence        = '';
    let lastDetectedChar    = '';
    let toastTimeout        = null;
    const CIRCUMFERENCE     = 2 * Math.PI * 26; // ≈ 163.4

    // ===================== PROGRESS RING =====================
    function setRingProgress(pct, mode) {
        const offset = CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE;
        progressRing.style.strokeDashoffset = offset;

        progressRing.classList.remove('complete', 'cooldown', 'number');
        if (mode === 'complete')  progressRing.classList.add('complete');
        else if (mode === 'cooldown') progressRing.classList.add('cooldown');
        else if (mode === 'number')   progressRing.classList.add('number');
    }

    // ===================== STATUS INDICATOR =====================
    function updateStatusIndicator(data) {
        const char = data.detected_char;
        const prog = data.stability_progress || 0;
        const cool = data.is_cooldown || false;
        const two  = data.two_hand_mode;

        // Two-hand mode badge
        twoHandBadge.classList.toggle('visible', two);

        if (!isCapturing) {
            setRingProgress(0, '');
            charCenter.textContent = '⏸';
            statusChar.textContent = '—';
            updateStateLabel('waiting', 'متوقف مؤقتاً');
            return;
        }

        // Cooldown: still show the last char but with orange ring
        if (cool) {
            setRingProgress(100, 'cooldown');
            if (char) {
                charCenter.textContent = char;
                statusChar.textContent = char;
            }
            updateStateLabel('cooldown', '⏳ جاهز للتالي');
            return;
        }

        if (!char) {
            setRingProgress(0, '');
            charCenter.textContent = two ? '#' : '?';
            statusChar.textContent = two ? 'ضع اليدين' : '—';
            updateStateLabel('waiting', two ? 'في انتظار إشارة الرقم' : 'في انتظار الإشارة');
            return;
        }

        charCenter.textContent = char;
        statusChar.textContent = two ? `#${char}` : char;

        // Orange ring for numbers, blue for letters
        const ringMode = prog >= 100 ? 'complete' : (two ? 'number' : '');

        if (prog >= 100) {
            setRingProgress(100, 'complete');
            updateStateLabel('done', '✓ تم التسجيل');
        } else if (prog > 0) {
            setRingProgress(prog, two ? 'number' : '');
            updateStateLabel('progress', `ثبّت يدك… ${Math.round(prog)}%`);
        } else {
            setRingProgress(0, '');
            updateStateLabel('waiting', 'في انتظار الثبات');
        }
    }

    function updateStateLabel(mode, text) {
        statusState.className = 'status-state';
        if (mode === 'waiting')   statusState.classList.add('waiting');
        else if (mode === 'done') statusState.classList.add('done');
        else if (mode === 'cooldown') statusState.classList.add('cooldown');

        statusState.innerHTML = `<span class="dot-pulse"></span>${text}`;
    }

    // ===================== SENTENCE DISPLAY =====================
    function renderSentence(sentence) {
        if (sentence === lastSentence) return;

        const prev = lastSentence;
        lastSentence = sentence;

        // Render as plain text so Arabic letters join correctly
        sentenceDisplay.innerText = sentence;

        // If new chars were added → flash glow animation
        if (sentence.length > prev.length) {
            const newChar = sentence.slice(prev.length).trim();
            sentenceDisplay.classList.remove('sentence-flash');
            // Force reflow to restart animation
            void sentenceDisplay.offsetWidth;
            sentenceDisplay.classList.add('sentence-flash');

            // Show toast for the last confirmed real character
            if (newChar && newChar !== ' ') {
                showConfirmToast(newChar[newChar.length - 1]);
            }
        }
    }

    // ===================== CONFIRM TOAST =====================
    function showConfirmToast(char) {
        clearTimeout(toastTimeout);
        toastChar.textContent = char;
        confirmToast.classList.remove('hide');
        confirmToast.classList.add('show');
        toastTimeout = setTimeout(() => {
            confirmToast.classList.replace('show', 'hide');
        }, 700);
    }

    // ===================== CAPTURE TOGGLE =====================
    function updateCaptureUI() {
        if (isCapturing) {
            btnToggleCapture.classList.replace('inactive', 'active');
            btnToggleCapture.innerHTML = '<i class="fas fa-video"></i>';
        } else {
            btnToggleCapture.classList.replace('active', 'inactive');
            btnToggleCapture.innerHTML = '<i class="fas fa-video-slash"></i>';
        }
    }

    btnToggleCapture.addEventListener('click', () => {
        fetch('/toggle_capture', { method: 'POST' })
            .then(r => r.ok && (isCapturing = !isCapturing, updateCaptureUI()));
    });

    // ===================== CONTROLS =====================
    btnSpeak.addEventListener('click', () => fetch('/speak', { method: 'POST' }));

    btnClearChar.addEventListener('click', () =>
        fetch('/clear', { method: 'POST' }).then(() => fetchStatus())
    );

    btnClear.addEventListener('click', () =>
        fetch('/clear_all', { method: 'POST' }).then(() => {
            lastSentence = '';
            sentenceDisplay.innerHTML = '';
        })
    );

    // ===================== KEYBOARD SHORTCUTS =====================
    document.addEventListener('keydown', (e) => {
        if (['Space','Backspace'].includes(e.code)) e.preventDefault();
        switch (e.code) {
            case 'KeyC': btnToggleCapture.click(); break;
            case 'Backspace': fetch('/clear', { method: 'POST' }).then(() => fetchStatus()); break;
            case 'Space': fetch('/add_space', { method: 'POST' }).then(() => fetchStatus()); break;
            case 'KeyS': fetch('/speak', { method: 'POST' }); break;
            case 'KeyF': btnClear.click(); break;
        }
    });

    // ===================== MAIN POLL =====================
    function fetchStatus() {
        fetch('/get_status')
            .then(r => r.json())
            .then(data => {
                renderSentence(data.sentence || '');
                updateStatusIndicator(data);

                if (data.is_capturing !== isCapturing) {
                    isCapturing = data.is_capturing;
                    updateCaptureUI();
                }
            })
            .catch(() => {});
    }

    setInterval(fetchStatus, 200);
    fetchStatus();
});
