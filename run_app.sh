#!/bin/bash
# سكريبت التشغيل السريع لتطبيق مترجم لغة الإشارة
echo "🚀 جاري تشغيل مترجم لغة الإشارة..."
cd "$(dirname "$0")"
source venv/bin/activate
python web_app.py
