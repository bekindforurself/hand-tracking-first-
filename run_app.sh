#!/bin/bash
# سكريبت التشغيل السريع لتطبيق مترجم لغة الإشارة
echo "🚀 جاري ضبط وإعداد الصوت (HDMI & Audio Jack)..."

# جلب أسماء المتحكمات المتوفرة في النظام لفتحها جميعاً
# هذا سيضمن فتح الصوت سواء كنت تستخدم HDMI أو سماعة خارجية (Headphone/PCM)
for control in "PCM" "HDMI" "Headphone" "Master" "Speaker"; do
    amixer sset "$control" 100% unmute >/dev/null 2>&1
    amixer -c 0 sset "$control" 100% unmute >/dev/null 2>&1
    amixer -c 1 sset "$control" 100% unmute >/dev/null 2>&1
done

echo "🚀 جاري تشغيل مترجم لغة الإشارة..."
cd "$(dirname "$0")"
source venv/bin/activate
python web_app.py
