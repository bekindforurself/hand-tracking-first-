import cv2
import mediapipe as mp

# 1. إعداد أدوات MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# 2. تشغيل الكاميرا
cap = cv2.VideoCapture(0)

print("جاري تشغيل الكاميرا... اضغط 'q' للخروج")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # 3. معالجة الصورة
    # MediaPipe يحتاج الصور بصيغة RGB و OpenCV يلتقطها BGR
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # 4. رسم النقاط إذا تم اكتشاف يد
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # رسم الروابط بين النقاط
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            
            # مثال: الوصول لإحداثيات نقطة معينة (نهاية الإبهام هي النقطة رقم 4)
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if id == 4: # رأس الإبهام
                    cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

    # 5. عرض النتيجة
    cv2.imshow("Hand Tracking Project - Mohammed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()