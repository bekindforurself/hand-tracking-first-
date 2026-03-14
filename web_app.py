import csv, copy, itertools, os, requests, json, threading, pygame, time, socket, cv2 as cv, numpy as np, asyncio, edge_tts
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision.core.image import Image as MpImage, ImageFormat

# --- Hands Wrapper using new Tasks API (mediapipe 0.10+) ---
class _HandLandmark:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

class _HandLandmarks:
    def __init__(self, lms):
        self.landmark = lms

class _HandsResult:
    def __init__(self, multi_hand_landmarks):
        self.multi_hand_landmarks = multi_hand_landmarks or []

class Hands:
    """Wrapper حول mediapipe HandLandmarker الجديد يحاكي واجهة solutions.hands.Hands القديمة"""
    _MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
    _MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")

    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5, model_complexity=0):
        if not os.path.exists(self._MODEL_PATH):
            print("[MediaPipe] تنزيل نموذج اليد... (مرة واحدة فقط)")
            import urllib.request
            urllib.request.urlretrieve(self._MODEL_URL, self._MODEL_PATH)
            print("[MediaPipe] تم تنزيل النموذج ✓")
        base_options = mp_python.BaseOptions(model_asset_path=self._MODEL_PATH)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
            running_mode=mp_vision.RunningMode.IMAGE
        )
        self._detector = mp_vision.HandLandmarker.create_from_options(options)

    def process(self, rgb_frame):
        mp_image = MpImage(image_format=ImageFormat.SRGB, data=rgb_frame)
        detection_result = self._detector.detect(mp_image)
        if not detection_result.hand_landmarks:
            return _HandsResult(None)
        multi = []
        for hand in detection_result.hand_landmarks:
            lms = [_HandLandmark(lm.x, lm.y, lm.z) for lm in hand]
            multi.append(_HandLandmarks(lms))
        return _HandsResult(multi)

    def close(self):
        self._detector.close()
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
# إعداد الصوت للرازبري باي
if os.name != 'nt': # Linux/RPi
    os.environ['SDL_AUDIODRIVER'] = 'alsa' # استخدام Linux ALSA

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
except Exception as e:
    print(f"[Audio] تعذر تهيئة Mixer: {e}")

def speak_text(text):
    if not text.strip(): return
    def run():
        try:
            # استخدام صوت "سلمى" أو "زارية" للهجة فصيحة ومرحة طبيعية
            VOICE = "ar-SA-HamedNeural" 
            # استخدام المسار المطلق لضمان عثور mpg123 على الملف
            base_dir = os.path.dirname(os.path.abspath(__file__))
            temp_file = os.path.join(base_dir, "temp_speech_web.mp3")
            
            async def generate_speech():
                communicate = edge_tts.Communicate(text, VOICE)
                await communicate.save(temp_file)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate_speech())
            loop.close()

            # انتظار بسيط جداً لضمان اكتمال الكتابة على القرص (مهم للرازبري)
            time.sleep(0.5)

            if not os.path.exists(temp_file):
                print(f"[Audio Error] الملف غير موجود: {temp_file}")
                return

            # محاولة التشغيل باستخدام mpg123 مع إجباره على استخدام ALSA (أضمن وسيلة للرازبري)
            played = False
            if os.name != 'nt': # Linux/RPi
                import subprocess
                try:
                    # -o alsa تجبره على استخدام نفس تعريف aplay الذي نجح معك
                    subprocess.run(["mpg123", "-o", "alsa", "-q", temp_file], check=True)
                    played = True
                except Exception as e:
                    print(f"[Audio] mpg123 failed: {e}")
            
            # إذا لم يعمل mpg123 أو كنا على وندوز، نستخدم pygame
            if not played:
                try:
                    pygame.mixer.music.load(temp_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    pygame.mixer.music.unload()
                except Exception as e:
                    print(f"[Audio] pygame failed: {e}")

            if os.path.exists(temp_file): os.remove(temp_file)
        except Exception as e: 
            print(f"[Audio Error] فشل محرك الصوت: {e}")
            if os.path.exists(temp_file): os.remove(temp_file)
    threading.Thread(target=run).start()

# --- محرك المعالجة الخلفي ---
def detection_thread():
    global state
    print("[Camera] بدأ تشغيل الكاميرا...")
    try:
        # محاولة فتح الكاميرا - التبديل التلقائي بين المدمجة والخارجية
        # فتح الكاميرا - يجرب عدة backends تلقائياً حتى يجد صورة فعلية
        cap = None
        camera_found = False
        backends_to_try = []
        if os.name == 'nt':  # Windows
            backends_to_try = [
                (0, cv.CAP_MSMF, "MSMF"),
                (0, cv.CAP_ANY, "AUTO"),
                (0, cv.CAP_DSHOW, "DSHOW"),
                (1, cv.CAP_MSMF, "MSMF-1"),
                (1, cv.CAP_ANY, "AUTO-1"),
            ]
        else:  # Linux/RPi
            backends_to_try = [(0, cv.CAP_ANY, "AUTO"), (1, cv.CAP_ANY, "AUTO-1")]

        for cam_idx, backend, bname in backends_to_try:
            try:
                c = cv.VideoCapture(cam_idx, backend)
                if c.isOpened():
                    ret, frame = c.read()
                    if ret and frame is not None:
                        cap = c
                        camera_index = cam_idx
                        print(f"[Camera] تم اكتشاف الكاميرا {cam_idx} [{bname}] ✓")
                        camera_found = True
                        break
                    else:
                        c.release()
                else:
                    c.release()
            except Exception:
                pass

        if not camera_found or cap is None:
            print("[Camera] ❌ لم يتم اكتشاف أي كاميرا! تأكد من توصيل الكاميرا والسماح للبرنامج باستخدامها.")
            return
            
        # دقة أخف للحصول على أداء أفضل على اللابتوب
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
        cap.set(cv.CAP_PROP_FPS, 20)

        # قراءات تجريبية للإحماء
        for _ in range(3):
            cap.read()

        # تهيئة MediaPipe Hands (باستخدام Tasks API الجديدة)
        hands = Hands(
            max_num_hands=1, 
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.5,
            model_complexity=0 
        )
        classifier = KeyPointClassifier(num_threads=4) # استخدام 4 أنوية للمعالجة
        with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
            labels = [row[0] for row in csv.reader(f)]

        print("[Camera] الكاميرا تعمل بنجاح ✓")
        
        frame_count = 0
        cooldown_until = 0 # منع القراءة المتكررة للحروف بسبب البطء
        last_results = None # حفظ آخر نتيجة لعرضها في الإطارات المخففة

        # إعدادات الأداء والجودة - فصل تام بين الويندوز والرازبري باي
        IS_WINDOWS = os.name == 'nt'
        if IS_WINDOWS:
            FRAME_SKIP = 1       # سرعة قصوى - معالجة كل إطار
            AI_SIZE = (480, 360) # نسخة ذهبية: أبعاد أكبر لدقة أعلى في التعرف
            STREAM_QUALITY = 85  # توازن الجودة
        else:
            FRAME_SKIP = 3       # توفير طاقة للرازبري باي
            AI_SIZE = (256, 192) # دقة منخفضة للذكاء الاصطناعي
            STREAM_QUALITY = 55  # جودة مضغوطة للشبكة

        while state.is_running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            frame = cv.flip(frame, 1)
            
            # المعالجة: وندوز يعالج كل شيء، الرازبري يتخطى
            if frame_count % FRAME_SKIP == 0:
                if AI_SIZE:
                    small_rgb = cv.resize(cv.cvtColor(frame, cv.COLOR_BGR2RGB), AI_SIZE)
                    last_results = hands.process(small_rgb)
                else:
                    # نسخة الويندوز الذهبية: معالجة الإطار بالحجم الكامل لأقصى دقة
                    last_results = hands.process(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
            
            results = last_results

            char_found = ""
            if results and results.multi_hand_landmarks and state.is_capturing:
                for hand_landmarks in results.multi_hand_landmarks:
                    h, w, _ = frame.shape
                    # numpy أسرع بكثير من deepcopy + itertools
                    lm_arr = np.array([[min(int(lm.x * w), w-1), min(int(lm.y * h), h-1)]
                                       for lm in hand_landmarks.landmark], dtype=np.float32)
                    landmark_list = lm_arr.astype(int).tolist()

                    norm = lm_arr - lm_arr[0]          # طرح نقطة الأساس
                    flat = norm.flatten()
                    max_val = np.abs(flat).max()
                    processed = (flat / max_val if max_val != 0 else flat).tolist()

                    char_id = classifier(processed)
                    char_found = labels[char_id]

                    # رسم المربع المحيط (Bounding Box) باللون الأسود
                    x_min, y_min = min([p[0] for p in landmark_list]), min([p[1] for p in landmark_list])
                    x_max, y_max = max([p[0] for p in landmark_list]), max([p[1] for p in landmark_list])
                    cv.rectangle(frame, (x_min - 10, y_min - 10), (x_max + 10, y_max + 10), (0, 0, 0), 1)

                    if state.blink_counter > 0:
                        if IS_WINDOWS:
                            # الوميض الذهبي الفائق: وميض منطقة اليد فقط لمنع الـ Lag
                            # بدلاً من نسخ الإطار بالكامل، نقوم بتفتيح منطقة اليد فقط
                            roi = frame[max(0, y_min-10):min(frame.shape[0], y_max+10), 
                                        max(0, x_min-10):min(frame.shape[1], x_max+10)]
                            if roi.size > 0:
                                white_rect = np.full(roi.shape, 255, dtype=np.uint8)
                                frame[max(0, y_min-10):min(frame.shape[0], y_max+10), 
                                      max(0, x_min-10):min(frame.shape[1], x_max+10)] = cv.addWeighted(roi, 0.5, white_rect, 0.5, 0)
                        else:
                            # الوميض المخفف للرازبري
                            frame[y_min:y_max, x_min:x_max] = cv.addWeighted(frame[y_min:y_max, x_min:x_max], 0.6, 
                                                                            np.full(frame[y_min:y_max, x_min:x_max].shape, 255, dtype=np.uint8), 0.4, 0)
                        state.blink_counter -= 1

                    # رسم الخطوط (Classic White Skeleton)
                    for i, j in [(2,3),(3,4),(5,6),(6,7),(7,8),(9,10),(10,11),(11,12),(13,14),(14,15),(15,16),(17,18),(18,19),(19,20),(0,1),(1,2),(2,5),(5,9),(9,13),(13,17),(17,0)]:
                        cv.line(frame, tuple(landmark_list[i]), tuple(landmark_list[j]), (255, 255, 255), 2, cv.LINE_AA)

                    # رسم النقاط (Classic White Circles)
                    for index, point in enumerate(landmark_list):
                        radius = 6 if index in [4, 8, 12, 16, 20] else 3
                        cv.circle(frame, tuple(point), radius, (255, 255, 255), -1, cv.LINE_AA)
                        cv.circle(frame, tuple(point), radius, (0, 0, 0), 1, cv.LINE_AA)

            with state.lock:
                state.detected_char = char_found
                
                if IS_WINDOWS:
                    # منطق الثبات الكلاسيكي (Golden Approach) - عداد الفريمات
                    if char_found == state.last_stable_char and char_found != "":
                        state.char_counter += 1
                    else:
                        state.char_counter = 0
                    
                    # 12 إطار ثبات = طباعة فورية وسريعة جداً (حوالي 0.4 ثانية)
                    if state.char_counter >= 12:
                        # تحويل 'أ' إلى 'ا' بناءً على طلبك
                        final_char = char_found
                        if final_char == "أ": final_char = "ا"
                        
                        if final_char == "مسافة": state.word_buffer += " "
                        elif final_char == "حذف": state.word_buffer = state.word_buffer[:-1]
                        else: state.word_buffer += final_char
                        
                        # الطريقة الذهبية: تشغيل التنبؤ في خلفية منفصلة لمنع الـ Lag
                        def update_suggestions_bg(buffer):
                            res = get_conversational_ai(buffer)
                            with state.lock:
                                state.suggestions = res
                        threading.Thread(target=update_suggestions_bg, args=(state.word_buffer,), daemon=True).start()
                        
                        state.blink_counter = 3
                        state.char_counter = 0
                else:
                    # منطق الثبات للرازبري - مبني على الوقت لمواجهة تذبذب الفريمات
                    if char_found == state.last_stable_char and char_found != "":
                        if state.stability_time == 0: state.stability_time = time.time()
                        if time.time() - state.stability_time >= 1.5 and time.time() > cooldown_until:
                            if char_found == "مسافة": state.word_buffer += " "
                            elif char_found == "حذف": state.word_buffer = state.word_buffer[:-1]
                            else: state.word_buffer += char_found
                            cooldown_until = time.time() + 2.0
                            state.suggestions = get_conversational_ai(state.word_buffer)
                            state.blink_counter = 3
                            state.stability_time = time.time()
                    else:
                        state.stability_time = 0
                
                state.last_stable_char = char_found

            # ضغط الإطار بالجودة المناسبة
            _, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, STREAM_QUALITY])
            with state.lock:
                state.current_frame = buffer.tobytes()

            # استراحة قصيرة جداً لمنع ثقل المعالج (مهمة جداً للسرعة)
            time.sleep(0.001)

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
            time.sleep(0.05) # 20 إطار/ثانية - مناسب للأداء
            
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
