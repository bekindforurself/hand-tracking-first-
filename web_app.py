import csv, copy, argparse, itertools, os, requests, json, threading, pygame, time, socket, cv2 as cv, numpy as np, mediapipe as mp, asyncio, edge_tts
from flask import Flask, render_template, Response, jsonify, request
import logging

from collections import Counter, deque
from model import KeyPointClassifier

app = Flask(__name__)

# إخفاء سجلات HTTP المتكررة لإبقاء التيرمنال نظيف
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# --- محرك التنبؤ الذكي (من app.py) ---
CONVERSATION_FILE = "arabic_conversation.json"
LOADED_DICT = {}
if os.path.exists(CONVERSATION_FILE):
    try:
        with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
            LOADED_DICT = json.load(f)
    except: pass

COMMON_WORDS = ["أنا", "أريد", "يذهب", "اذهب", "نذهب", "تذهب", "أين", "أحب", "أحتاج", "كيف", "مرحبا", "شكرا", "السلام", "هل", "في", "إلى", "من", "رايح", "بدي", "وين", "شو", "لو", "ان", "شاء", "الله", "يا", "اخي", "امي", "ابي", "تعبان", "جائع", "مريض", "بخير", "دكتور", "مستشفى", "حمام", "ماء", "اكل", "نوم"]

def normalize(text):
    return text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي").strip()

def get_conversational_ai(text):
    raw_text = text.strip()
    if not raw_text: return []
    words = raw_text.split()
    last_word = words[-1]
    last_word_norm = normalize(last_word)
    
    if not text.endswith(" "):
        completions = [w for w in COMMON_WORDS if normalize(w).startswith(last_word_norm)]
        if completions and len(completions[0]) > len(last_word):
            return completions[:4]

    for key, predictions in LOADED_DICT.items():
        if normalize(key) == last_word_norm:
            return predictions[:4]

    try:
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={raw_text}&hl=ar"
        resp = requests.get(url, timeout=0.8)
        if resp.status_code == 200:
            raw_cloud = json.loads(resp.text)[1]
            cloud_clean = []
            forbidden = ["اخبار", "طقس", "مباراة", "فيلم", "سعر", "يوتيوب"]
            for s in raw_cloud:
                if any(f in s for f in forbidden): continue 
                q_words = raw_text.split()
                s_words = s.split()
                idx = len(q_words) if text.endswith(" ") else len(q_words) - 1
                s_sug = " ".join(s_words[idx:]) if len(s_words) > idx else s
                if s_sug and len(s_sug.split()) <= 2:
                    cloud_clean.append(s_sug)
            return cloud_clean[:4]
    except: pass
    return []

# --- إعدادات النظام ---
class GlobalState:
    def __init__(self):
        self.word_buffer = ""
        self.detected_char = ""
        self.suggestions = []
        self.last_stable_char = ""
        self.char_counter = 0
        self.blink_counter = 0
        self.stability_time = 0 # تتبع وقت ثبات الحرف
        self.lock = threading.Lock()
        self.is_running = True
        self.is_capturing = True # حالة الالتقاط مفعلة افتراضياً
        # إطار أولي فارغ لمنع الشاشة السوداء
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        _, buf = cv.imencode('.jpg', blank)
        self.current_frame = buf.tobytes()

state = GlobalState()
pygame.mixer.init()

def speak_text(text):
    if not text.strip(): return
    def run():
        try:
            # استخدام صوت "سلمى" أو "زارية" للهجة فصيحة ومرحة طبيعية
            VOICE = "ar-SA-HamedNeural" 
            temp_file = "temp_speech_web.mp3"
            
            async def generate_speech():
                communicate = edge_tts.Communicate(text, VOICE)
                await communicate.save(temp_file)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate_speech())
            loop.close()

            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            if os.path.exists(temp_file): os.remove(temp_file)
        except Exception as e: print(f"Speech Engine Error: {e}")
    threading.Thread(target=run).start()

# --- محرك المعالجة الخلفي ---
def detection_thread():
    global state
    print("[Camera] بدأ تشغيل الكاميرا...")
    try:
        # محاولة فتح الكاميرا - التبديل التلقائي بين المدمجة والخارجية
        camera_index = 0
        if os.name == 'nt': # Windows
            cap = cv.VideoCapture(camera_index, cv.CAP_DSHOW)
        else: # Linux/Raspberry Pi
            cap = cv.VideoCapture(camera_index)

        if not cap.isOpened():
            print(f"[Camera] الكاميرا {camera_index} لم تفتح، نجرب الكاميرا التالية...")
            camera_index = 1
            cap = cv.VideoCapture(camera_index)
            
        # ضبط دقة الكاميرا لتحسين الأداء على الرازبري باي
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
        cap.set(cv.CAP_PROP_FPS, 30)

        # قراءات تجريبية للإحماء
        for _ in range(5):
            cap.read()

        # تحسين إعدادات MediaPipe للعمل بسرعة أكبر (Complexity=0 هو الأخف)
        hands = mp.solutions.hands.Hands(
            max_num_hands=1, 
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.5,
            model_complexity=0 
        )
        classifier = KeyPointClassifier(num_threads=4) # استخدام 4 أنوية للمعالجة
        with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
            labels = [row[0] for row in csv.reader(f)]

        print("[Camera] الكاميرا تعمل بنجاح ✓")

        while state.is_running:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv.flip(frame, 1)
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            char_found = ""
            if results.multi_hand_landmarks and state.is_capturing:
                for hand_landmarks in results.multi_hand_landmarks:
                    # رسم خطوط التتبع (Skeleton) لرؤيتها في المتصفح يتم يدوياً في الأسفل لضمان النظافة بدون نقاط
                    
                    landmark_list = []
                    h, w, _ = frame.shape
                    for landmark in hand_landmarks.landmark:
                        landmark_list.append([min(int(landmark.x * w), w - 1), min(int(landmark.y * h), h - 1)])

                    temp = copy.deepcopy(landmark_list)
                    base_x, base_y = temp[0][0], temp[0][1]
                    for i in range(len(temp)):
                        temp[i][0] -= base_x
                        temp[i][1] -= base_y
                    flat = list(itertools.chain.from_iterable(temp))
                    max_val = max(list(map(abs, flat)))
                    processed = [n / (max_val if max_val != 0 else 1) for n in flat]

                    char_id = classifier(processed)
                    char_found = labels[char_id]

                    # رسم المربع المحيط (Bounding Box) باللون الأسود
                    x_min, y_min = min([p[0] for p in landmark_list]), min([p[1] for p in landmark_list])
                    x_max, y_max = max([p[0] for p in landmark_list]), max([p[1] for p in landmark_list])
                    cv.rectangle(frame, (x_min - 10, y_min - 10), (x_max + 10, y_max + 10), (0, 0, 0), 1)

                    # تأثير الوميض من الداخل (Flash)
                    if state.blink_counter > 0:
                        overlay = frame.copy()
                        cv.rectangle(overlay, (x_min - 10, y_min - 10), (x_max + 10, y_max + 10), (255, 255, 255), -1)
                        cv.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
                        state.blink_counter -= 1

                    # رسم الخطوط (White Lines)
                    for i, j in [(2,3),(3,4),(5,6),(6,7),(7,8),(9,10),(10,11),(11,12),(13,14),(14,15),(15,16),(17,18),(18,19),(19,20),(0,1),(1,2),(2,5),(5,9),(9,13),(13,17),(17,0)]:
                        cv.line(frame, tuple(landmark_list[i]), tuple(landmark_list[j]), (255, 255, 255), 2)

                    # رسم النقاط (White Circles)
                    for index, point in enumerate(landmark_list):
                        radius = 6 if index in [4, 8, 12, 16, 20] else 3
                        cv.circle(frame, tuple(point), radius, (255, 255, 255), -1)
                        cv.circle(frame, tuple(point), radius, (0, 0, 0), 1) # إطار أسود رقيق للنقطة لتمييزها

            with state.lock:
                state.detected_char = char_found
                
                # منطق ثبات الحرف - يجب أن يثبت الحرف لمدة 1.5 ثانية (للمبتدئين)
                if char_found == state.last_stable_char and char_found != "":
                    if state.stability_time == 0:
                        state.stability_time = time.time()
                    
                    # إذا مرت 1.0 ثانية من الثبات الكامل
                    if time.time() - state.stability_time >= 1.0:
                        if char_found == "مسافة": state.word_buffer += " "
                        elif char_found == "حذف": state.word_buffer = state.word_buffer[:-1]
                        else: state.word_buffer += char_found
                        
                        state.suggestions = get_conversational_ai(state.word_buffer)
                        state.blink_counter = 3 # وميض للتأكيد
                        state.stability_time = time.time() # البدء بالحساب للمرة القادمة إذا استمر بالثبات
                else:
                    state.stability_time = 0
                
                state.last_stable_char = char_found

            # ضغط الإطار فقط إذا كان هناك تغيير (لتقليل استهلاك المعالج)
            _, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
            with state.lock:
                state.current_frame = buffer.tobytes()

        cap.release()
        print("[Camera] تم إيقاف الكاميرا.")
    except Exception as e:
        print(f"[Camera] خطأ في الـ detection thread: {e}")
        import traceback; traceback.print_exc()

# --- مسارات Flask ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """مسار بث الفيديو المباشر (MJPEG)"""
    def generate():
        while True:
            with state.lock:
                frame = state.current_frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.03) # حوالي 30 فريم في الثانية حد أقصى
            
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snapshot')
def snapshot():
    """إرجاع إطار واحد من الكاميرا كصورة JPEG"""
    with state.lock:
        return Response(state.current_frame, mimetype='image/jpeg')

@app.route('/get_status')
def get_status():
    with state.lock:
        return jsonify({
            "sentence": state.word_buffer,
            "detected_char": state.detected_char,
            "suggestions": state.suggestions,
            "is_capturing": state.is_capturing
        })

@app.route('/toggle_capture', methods=['POST'])
def toggle_capture():
    with state.lock:
        state.is_capturing = not state.is_capturing
    return jsonify({"status": "ok", "is_capturing": state.is_capturing})

@app.route('/speak', methods=['POST'])
def speak():
    speak_text(state.word_buffer)
    return "OK"

@app.route('/clear', methods=['POST'])
def clear():
    """حذف آخر حرف (Backspace)"""
    with state.lock:
        state.word_buffer = state.word_buffer[:-1]
        state.suggestions = []
    return "OK"

@app.route('/clear_all', methods=['POST'])
def clear_all():
    """مسح كل الجملة"""
    with state.lock:
        state.word_buffer = ""
        state.suggestions = []
    return "OK"

@app.route('/add_space', methods=['POST'])
def add_space():
    """إضافة مسافة"""
    with state.lock:
        state.word_buffer += " "
        state.suggestions = get_conversational_ai(state.word_buffer)
    return "OK"

@app.route('/select_suggestion', methods=['POST'])
def select_suggestion():
    word = request.args.get('word')
    if word:
        with state.lock:
            words = state.word_buffer.strip().split()
            if not state.word_buffer.endswith(" ") and words:
                words[-1] = word
                state.word_buffer = " ".join(words) + " "
            else:
                state.word_buffer = state.word_buffer.strip() + " " + word + " "
            state.suggestions = []
    return "OK"

@app.route('/finish', methods=['POST'])
def finish():
    with state.lock:
        # يمكن إضافة منطق لحفظ الجملة أو إرسالها لمكان آخر
        state.word_buffer += ". "
    return "OK"

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """إيقاف السيرفر من الواجهة"""
    state.is_running = False
    os._exit(0)
    return "Shutting down..."

def get_ip_address():
    """جلب عنوان الـ IP المحلي للجهاز"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # لا يشترط وجود اتصال فعلي بهذا العنوان، فقط لفتح الـ socket
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    local_ip = get_ip_address()
    print("\n" + "="*50)
    print(f"🚀 Sign Language App is starting!")
    print(f"🔗 Access it from any device on your network at:")
    print(f"👉 http://{local_ip}:5000")
    print("="*50 + "\n")
    
    threading.Thread(target=detection_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
