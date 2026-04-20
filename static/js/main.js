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
            case 'Digit0': case 'Numpad0': recordNumber(0); break;
            case 'Digit1': case 'Numpad1': recordNumber(1); break;
            case 'Digit2': case 'Numpad2': recordNumber(2); break;
            case 'Digit3': case 'Numpad3': recordNumber(3); break;
            case 'Digit4': case 'Numpad4': recordNumber(4); break;
            case 'Digit5': case 'Numpad5': recordNumber(5); break;
            case 'Digit6': case 'Numpad6': recordNumber(6); break;
            case 'Digit7': case 'Numpad7': recordNumber(7); break;
            case 'Digit8': case 'Numpad8': recordNumber(8); break;
            case 'Digit9': case 'Numpad9': recordNumber(9); break;
            case 'KeyX': recordNumber(10); break;
            case 'KeyY': 
                fetch('/record_now?label=38&type=single', { method: 'POST' });
                showToast("جاري تسجيل: ئ");
                break;
        }
    });

    function recordNumber(n) {
        fetch(`/record_now?label=${n}&type=dual`, { method: 'POST' });
        showToast(`جاري تسجيل الرقم: ${n}`);
    }

    function showToast(message) {
        const toast = document.createElement('div');
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.left = '50%';
        toast.style.transform = 'translateX(-50%)';
        toast.style.background = 'rgba(0,0,0,0.8)';
        toast.style.color = '#fff';
        toast.style.padding = '10px 25px';
        toast.style.borderRadius = '30px';
        toast.style.zIndex = '9999';
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 1000);
    }

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

                // التعامل مع وضع اليدين (الأرقام)
                if (data.two_hand_mode) {
                    detectedCharDisplay.innerText = "وضع الأرقام 🔢";
                    detectedCharDisplay.style.color = "#ff9800"; // لون برتقالي مميز للوضعية
                } else if (isCapturing) {
                    detectedCharDisplay.innerText = `الحرف: ${data.detected_char || "..."}`;
                    detectedCharDisplay.style.color = "white";
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
