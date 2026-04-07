import cv2 as cv
import time

print("🔍 البحث عن الكاميرات المتاحة (بدون DSHOW)...")
found = False

backends = [
    (cv.CAP_ANY, "AUTO"),
    (cv.CAP_MSMF, "MSMF"),
    (cv.CAP_DSHOW, "DSHOW"),
]

for backend, name in backends:
    for i in range(3):
        try:
            if backend == cv.CAP_ANY:
                cap = cv.VideoCapture(i)
            else:
                cap = cv.VideoCapture(i, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ [{name}] الكاميرا رقم {i} تعمل! - الدقة: {int(cap.get(cv.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))}")
                    found = True
                else:
                    print(f"⚠️ [{name}] الكاميرا رقم {i}: مفتوحة لكن لا صورة")
                cap.release()
        except Exception as e:
            print(f"❌ [{name}] كاميرا {i}: خطأ - {e}")

if not found:
    print("\n❌ لا توجد كاميرا متاحة!")
    print("تحقق من:")
    print("  - ابدأ > الإعدادات > الخصوصية والأمان > الكاميرا")
    print("  - تأكد أن خيار 'السماح للتطبيقات بالوصول إلى الكاميرا' مفعّـل")
else:
    print("\n✅ تم اكتشاف كاميرا!")
