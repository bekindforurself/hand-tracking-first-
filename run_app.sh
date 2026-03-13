#!/bin/bash
# سكريبت التشغيل السريع لتطبيق مترجم لغة الإشارة
echo "🚀 جاري فحص وإعداد الصوت..."

# محاولة فك الكتم ورفع الصوت باستخدام كل الأسماء المحتملة في الرازبري باي
for control in "Master" "PCM" "HDMI" "Headphone" "Speaker"; do
    amixer -c 0 sset "$control" 100% unmute >/dev/null 2>&1
    amixer -c 1 sset "$control" 100% unmute >/dev/null 2>&1
done

echo "🚀 جاري تشغيل مترجم لغة الإشارة..."
cd "$(dirname "$0")"
source venv/bin/activate
python web_app.py
