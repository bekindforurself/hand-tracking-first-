import csv, copy, argparse, itertools, os, requests, json, threading, pygame, time, cv2 as cv, numpy as np, mediapipe as mp
from flask import Flask, render_template, Response, jsonify, request
import logging

from gtts import gTTS
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
        self.lock = threading.Lock()
        self.is_running = True
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
            tts = gTTS(text=text, lang='ar')
            temp_file = "temp_speech_web.mp3"
            tts.save(temp_file)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            if os.path.exists(temp_file): os.remove(temp_file)
        except Exception as e: print(f"TTS Error: {e}")
    threading.Thread(target=run).start()

# --- محرك المعالجة الخلفي ---
def detection_thread():
    global state
    print("[Camera] بدأ تشغيل الكاميرا...")
    try:
        cap = cv.VideoCapture(0, cv.CAP_DSHOW)  # DirectShow for Windows USB cameras
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv.CAP_PROP_FPS, 30)
        if not cap.isOpened():
            print("[Camera] خطأ: لا يمكن فتح الكاميرا! تأكد أنها غير مستخدمة من برنامج آخر.")
            return
        # قراءات تجريبية للإحماء
        for _ in range(5):
            cap.read()

        hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        classifier = KeyPointClassifier()
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
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # رسم خطوط التتبع (Skeleton) لرؤيتها في المتصفح يتم يدوياً في الأسفل لضمان النظافة بدون نقاط
                    
                    landmark_list = []
                    for landmark in hand_landmarks.landmark:
                        landmark_list.append([min(int(landmark.x * 640), 639), min(int(landmark.y * 480), 479)])

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

                    for i, j in [(2,3),(3,4),(5,6),(6,7),(7,8),(9,10),(10,11),(11,12),(13,14),(14,15),(15,16),(17,18),(18,19),(19,20),(0,1),(1,2),(2,5),(5,9),(9,13),(13,17),(17,0)]:
                        cv.line(frame, tuple(landmark_list[i]), tuple(landmark_list[j]), (255, 255, 255), 2)

            with state.lock:
                state.detected_char = char_found
                
                if char_found == state.last_stable_char and char_found != "":
                    state.char_counter += 1
                else:
                    state.char_counter = 0
                state.last_stable_char = char_found

                if state.char_counter == 18:
                    if char_found == "مسافة": state.word_buffer += " "
                    elif char_found == "حذف": state.word_buffer = state.word_buffer[:-1]
                    else: state.word_buffer += char_found
                    state.suggestions = get_conversational_ai(state.word_buffer)
                    state.char_counter = 0

            _, buffer = cv.imencode('.jpg', frame)
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

@app.route('/snapshot')
def snapshot():
    """إرجاع إطار واحد من الكاميرا كصورة JPEG"""
    response = Response(state.current_frame, mimetype='image/jpeg')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/get_status')
def get_status():
    with state.lock:
        return jsonify({
            "sentence": state.word_buffer,
            "detected_char": state.detected_char,
            "suggestions": state.suggestions
        })

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

if __name__ == '__main__':
    threading.Thread(target=detection_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
