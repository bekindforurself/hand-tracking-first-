document.addEventListener('DOMContentLoaded', () => {
    const sentenceDisplay = document.getElementById('sentence-display');
    const detectedCharDisplay = document.getElementById('detected-char');
    const suggestionsContainer = document.getElementById('suggestions');
    const btnSpeak = document.getElementById('btn-speak');
    const btnClear = document.getElementById('btn-clear');
    const btnFinish = document.getElementById('btn-finish');
    const btnToggleCapture = document.getElementById('btn-toggle-capture');
    const videoFeed = document.getElementById('video-feed');

    let lastDetectedChar = "";
    let activeSuggestionIndex = 0; // المؤشر الحالي للاقتراحات
    let currentSuggestions = [];
    let isCapturing = true;


    // تبديل حالة الالتقاط
    function toggleCapture() {
        fetch('/toggle_capture', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                isCapturing = data.is_capturing;
                updateCaptureUI();
            });
    }

    function updateCaptureUI() {
        if (isCapturing) {
            btnToggleCapture.classList.remove('inactive');
            btnToggleCapture.classList.add('active');
            btnToggleCapture.innerHTML = '<i class="fas fa-video"></i>';
            detectedCharDisplay.style.display = 'block';
        } else {
            btnToggleCapture.classList.remove('active');
            btnToggleCapture.classList.add('inactive');
            btnToggleCapture.innerHTML = '<i class="fas fa-video-slash"></i>';
            detectedCharDisplay.style.display = 'none';
        }
    }

    btnToggleCapture.onclick = toggleCapture;

    // --- اختصارات لوحة المفاتيح ---
    document.addEventListener('keydown', (e) => {
        if (['Space', 'Backspace', 'ArrowLeft', 'ArrowRight', 'Enter'].includes(e.code)) e.preventDefault();

        switch (e.code) {
            case 'KeyC': // حرف C لتشغيل/إيقاف الالتقاط
                toggleCapture();
                break;
            case 'Backspace':
                fetch('/clear', { method: 'POST' }).then(() => updateUI());
                break;
            case 'Space':
                fetch('/add_space', { method: 'POST' }).then(() => updateUI());
                break;
            case 'Enter':
                if (currentSuggestions.length > 0) {
                    selectSuggestion(currentSuggestions[activeSuggestionIndex]);
                }
                break;
            case 'ArrowLeft': // التالي في RTL
                if (currentSuggestions.length > 0) {
                    activeSuggestionIndex = (activeSuggestionIndex + 1) % currentSuggestions.length;
                    renderPills();
                }
                break;
            case 'ArrowRight': // السابق في RTL
                if (currentSuggestions.length > 0) {
                    activeSuggestionIndex = (activeSuggestionIndex - 1 + currentSuggestions.length) % currentSuggestions.length;
                    renderPills();
                }
                break;
            case 'KeyS':
                fetch('/speak', { method: 'POST' });
                break;
            case 'KeyF': // إنهاء الجملة (مسح الكل)
                fetch('/clear_all', { method: 'POST' }).then(() => updateUI());
                break;
            case 'Digit1': case 'Numpad1':
            case 'Digit2': case 'Numpad2':
            case 'Digit3': case 'Numpad3':
            case 'Digit4': case 'Numpad4':
                const idx = parseInt(e.key) - 1;
                const pills = document.querySelectorAll('.suggestion-pill');
                if (pills[idx]) pills[idx].click();
                break;
        }
    });

    // --- تفعيل بث الفيديو المستمر (أسرع بكثير للرازبري باي) ---
    videoFeed.src = '/video_feed';

    // دالة رسم الاقتراحات لضمان تحديث الـ active class فوراً
    function renderPills() {
        suggestionsContainer.innerHTML = '';
        currentSuggestions.forEach((sug, index) => {
            const pill = document.createElement('div');
            pill.className = 'suggestion-pill';
            if (index === activeSuggestionIndex) pill.classList.add('active');
            pill.innerText = sug;
            pill.onclick = () => selectSuggestion(sug);
            suggestionsContainer.appendChild(pill);
        });
    }

    // --- تحديث الواجهة ---
    function updateUI() {
        fetch('/get_status')
            .then(response => response.json())
            .then(data => {
                sentenceDisplay.innerText = data.sentence || "";

                if (data.is_capturing !== isCapturing) {
                    isCapturing = data.is_capturing;
                    updateCaptureUI();
                }

                if (isCapturing) {
                    detectedCharDisplay.innerText = `الحرف: ${data.detected_char || "..."}`;
                }

                if (data.detected_char && data.detected_char !== lastDetectedChar) {
                    lastDetectedChar = data.detected_char;
                }

                // إذا تغيرت الاقتراحات، نعيد ضبط المؤشر
                if (JSON.stringify(data.suggestions) !== JSON.stringify(currentSuggestions)) {
                    currentSuggestions = data.suggestions || [];
                    activeSuggestionIndex = 0;
                    renderPills();
                }
            })
            .catch(err => console.error('Status fetch error:', err));
    }

    function selectSuggestion(word) {
        fetch(`/select_suggestion?word=${encodeURIComponent(word)}`, { method: 'POST' })
            .then(() => {
                currentSuggestions = []; // مسح الاقتراحات بعد الاختيار
                updateUI();
            });
    }

    btnSpeak.onclick = () => { fetch('/speak', { method: 'POST' }); };
    btnClear.onclick = () => { fetch('/clear', { method: 'POST' }).then(() => updateUI()); };
    btnFinish.onclick = () => { fetch('/clear_all', { method: 'POST' }).then(() => updateUI()); };

    setInterval(updateUI, 300);
});
