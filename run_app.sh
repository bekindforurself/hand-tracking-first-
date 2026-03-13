#!/bin/bash
# سكريبت التشغيل السريع لتطبيق مترجم لغة الإشارة
echo "🚀 جاري ضبط مخرج الصوت (PCM)..."

# فتح الصوت ورفعه للحد الأقصى لمخرج PCM المكتشف في جهازك
amixer sset 'PCM' 100% unmute >/dev/null 2>&1
amixer -c 0 sset 'PCM' 100% unmute >/dev/null 2>&1
amixer -c 1 sset 'PCM' 100% unmute >/dev/null 2>&1

echo "🚀 جاري تشغيل مترجم لغة الإشارة..."
cd "$(dirname "$0")"
source venv/bin/activate
python web_app.py
