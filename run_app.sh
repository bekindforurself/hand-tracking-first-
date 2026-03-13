#!/bin/bash
# سكريبت التشغيل السريع لتطبيق مترجم لغة الإشارة
echo "🚀 جاري فحص وإعداد الصوت..."
# فتح الصوت وفك الكتم تلقائياً (لحل مشكلة اختفاء الصوت في الرازبري)
amixer -c 0 sset Master 100% unmute >/dev/null 2>&1 || amixer -c 1 sset Master 100% unmute >/dev/null 2>&1
amixer -c 0 sset PCM 100% >/dev/null 2>&1 || amixer -c 1 sset PCM 100% >/dev/null 2>&1

echo "🚀 جاري تشغيل مترجم لغة الإشارة..."
cd "$(dirname "$0")"
source venv/bin/activate
python web_app.py
