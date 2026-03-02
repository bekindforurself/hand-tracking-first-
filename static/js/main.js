document.addEventListener('DOMContentLoaded', () => {
    const sentenceDisplay = document.getElementById('sentence-display');
    const detectedCharDisplay = document.getElementById('detected-char');
    const suggestionsContainer = document.getElementById('suggestions');
    const btnSpeak = document.getElementById('btn-speak');
    const btnClear = document.getElementById('btn-clear');
    const btnClearAll = document.getElementById('btn-clear-all');
    const btnShutdown = document.getElementById('btn-shutdown');
    const videoFeed = document.getElementById('video-feed');

    // زر الإيقاف
    btnShutdown.onclick = () => {
        if (confirm('هل أنت متأكد من إيقاف التطبيق؟')) {
            fetch('/shutdown', { method: 'POST' })
                .catch(() => { }); // الاتصال سينتهي مع السيرفر
            btnShutdown.innerText = '⏹ جارِ الإيقاف...';
            btnShutdown.disabled = true;
        }
    };

    // --- اختصارات لوحة المفاتيح ---
    document.addEventListener('keydown', (e) => {
        // منع تأثيرات المتصفح الافتراضية
        if (['Space', 'Backspace'].includes(e.code)) e.preventDefault();

        switch (e.code) {
            case 'Backspace':
                fetch('/clear', { method: 'POST' }).then(() => updateUI());
                break;
            case 'Space':
                fetch('/add_space', { method: 'POST' }).then(() => updateUI());
                break;
            case 'KeyS':
                fetch('/speak', { method: 'POST' });
                break;
            case 'KeyN':
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

    // --- تحديث الكاميرا كل 80ms (snapshot polling) ---
    function refreshCamera() {
        const newSrc = '/snapshot?t=' + Date.now();
        const img = new Image();
        img.onload = () => {
            videoFeed.src = newSrc;
            setTimeout(refreshCamera, 80);
        };
        img.onerror = () => {
            setTimeout(refreshCamera, 200); // إعادة المحاولة عند الخطأ
        };
        img.src = newSrc;
    }
    refreshCamera();

    // --- تحديث واجهة النص والاقتراحات ---
    function updateUI() {
        fetch('/get_status')
            .then(response => response.json())
            .then(data => {
                sentenceDisplay.innerText = data.sentence || "";
                detectedCharDisplay.innerText = `الحرف: ${data.detected_char || "..."}`;

                if (data.suggestions && data.suggestions.length > 0) {
                    suggestionsContainer.innerHTML = '';
                    data.suggestions.forEach((sug, index) => {
                        const pill = document.createElement('div');
                        pill.className = 'suggestion-pill';
                        if (index === 0) pill.classList.add('active');
                        pill.innerText = sug;
                        pill.onclick = () => selectSuggestion(sug);
                        suggestionsContainer.appendChild(pill);
                    });
                } else {
                    suggestionsContainer.innerHTML = '';
                }
            })
            .catch(err => console.error('Status fetch error:', err));
    }

    function selectSuggestion(word) {
        fetch(`/select_suggestion?word=${encodeURIComponent(word)}`, { method: 'POST' })
            .then(() => updateUI());
    }

    btnSpeak.onclick = () => { fetch('/speak', { method: 'POST' }); };

    // حذف آخر حرف (Backspace)
    btnClear.onclick = () => {
        fetch('/clear', { method: 'POST' }).then(() => updateUI());
    };

    // مسح كل الجملة
    btnClearAll.onclick = () => {
        fetch('/clear_all', { method: 'POST' }).then(() => updateUI());
    };

    setInterval(updateUI, 300);
});
