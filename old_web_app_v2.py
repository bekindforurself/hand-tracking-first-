import csv, copy, argparse, itertools, os, requests, json, threading, pygame, time, cv2 as cv, numpy as np, mediapipe as mp, asyncio, edge_tts
from flask import Flask, render_template, Response, jsonify, request
import logging

from collections import Counter, deque
from model import KeyPointClassifier

app = Flask(__name__)

# ╪Ñ╪«┘ü╪º╪í ╪│╪¼┘ä╪º╪¬ HTTP ╪º┘ä┘à╪¬┘â╪▒╪▒╪⌐ ┘ä╪Ñ╪¿┘é╪º╪í ╪º┘ä╪¬┘è╪▒┘à┘å╪º┘ä ┘å╪╕┘è┘ü
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# --- ┘à╪¡╪▒┘â ╪º┘ä╪¬┘å╪¿╪ñ ╪º┘ä╪░┘â┘è (┘à┘å app.py) ---
CONVERSATION_FILE = "arabic_conversation.json"
LOADED_DICT = {}
if os.path.exists(CONVERSATION_FILE):
    try:
        with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
            LOADED_DICT = json.load(f)
    except: pass

COMMON_WORDS = ["╪ú┘å╪º", "╪ú╪▒┘è╪»", "┘è╪░┘ç╪¿", "╪º╪░┘ç╪¿", "┘å╪░┘ç╪¿", "╪¬╪░┘ç╪¿", "╪ú┘è┘å", "╪ú╪¡╪¿", "╪ú╪¡╪¬╪º╪¼", "┘â┘è┘ü", "┘à╪▒╪¡╪¿╪º", "╪┤┘â╪▒╪º", "╪º┘ä╪│┘ä╪º┘à", "┘ç┘ä", "┘ü┘è", "╪Ñ┘ä┘ë", "┘à┘å", "╪▒╪º┘è╪¡", "╪¿╪»┘è", "┘ê┘è┘å", "╪┤┘ê", "┘ä┘ê", "╪º┘å", "╪┤╪º╪í", "╪º┘ä┘ä┘ç", "┘è╪º", "╪º╪«┘è", "╪º┘à┘è", "╪º╪¿┘è", "╪¬╪╣╪¿╪º┘å", "╪¼╪º╪ª╪╣", "┘à╪▒┘è╪╢", "╪¿╪«┘è╪▒", "╪»┘â╪¬┘ê╪▒", "┘à╪│╪¬╪┤┘ü┘ë", "╪¡┘à╪º┘à", "┘à╪º╪í", "╪º┘â┘ä", "┘å┘ê┘à"]

def normalize(text):
    return text.replace("╪ú", "╪º").replace("╪Ñ", "╪º").replace("╪ó", "╪º").replace("╪⌐", "┘ç").replace("┘ë", "┘è").strip()

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
            forbidden = ["╪º╪«╪¿╪º╪▒", "╪╖┘é╪│", "┘à╪¿╪º╪▒╪º╪⌐", "┘ü┘è┘ä┘à", "╪│╪╣╪▒", "┘è┘ê╪¬┘è┘ê╪¿"]
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

# --- ╪Ñ╪╣╪»╪º╪»╪º╪¬ ╪º┘ä┘å╪╕╪º┘à ---
class GlobalState:
    def __init__(self):
        self.word_buffer = ""
        self.detected_char = ""
        self.suggestions = []
        self.last_stable_char = ""
        self.char_counter = 0
        self.blink_counter = 0
        self.lock = threading.Lock()
        self.is_running = True
        self.is_capturing = True # ╪¡╪º┘ä╪⌐ ╪º┘ä╪º┘ä╪¬┘é╪º╪╖ ┘à┘ü╪╣┘ä╪⌐ ╪º┘ü╪¬╪▒╪º╪╢┘è╪º┘ï
        # ╪Ñ╪╖╪º╪▒ ╪ú┘ê┘ä┘è ┘ü╪º╪▒╪║ ┘ä┘à┘å╪╣ ╪º┘ä╪┤╪º╪┤╪⌐ ╪º┘ä╪│┘ê╪»╪º╪í
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        _, buf = cv.imencode('.jpg', blank)
        self.current_frame = buf.tobytes()

state = GlobalState()
pygame.mixer.init()

def speak_text(text):
    if not text.strip(): return
    def run():
        try:
            # ╪º╪│╪¬╪«╪»╪º┘à ╪╡┘ê╪¬ "╪│┘ä┘à┘ë" ╪ú┘ê "╪▓╪º╪▒┘è╪⌐" ┘ä┘ä┘ç╪¼╪⌐ ┘ü╪╡┘è╪¡╪⌐ ┘ê┘à╪▒╪¡╪⌐ ╪╖╪¿┘è╪╣┘è╪⌐
            VOICE = "ar-SA-ZariyahNeural" 
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

# --- ┘à╪¡╪▒┘â ╪º┘ä┘à╪╣╪º┘ä╪¼╪⌐ ╪º┘ä╪«┘ä┘ü┘è ---
def detection_thread():
    global state
    print("[Camera] ╪¿╪»╪ú ╪¬╪┤╪║┘è┘ä ╪º┘ä┘â╪º┘à┘è╪▒╪º...")
    try:
        # ┘à╪¡╪º┘ê┘ä╪⌐ ┘ü╪¬╪¡ ╪º┘ä┘â╪º┘à┘è╪▒╪º - ╪º┘ä╪¬╪¿╪»┘è┘ä ╪º┘ä╪¬┘ä┘é╪º╪ª┘è ╪¿┘è┘å ╪º┘ä┘à╪»┘à╪¼╪⌐ ┘ê╪º┘ä╪«╪º╪▒╪¼┘è╪⌐
        camera_index = 0
        if os.name == 'nt': # Windows
            cap = cv.VideoCapture(camera_index, cv.CAP_DSHOW)
        else: # Linux/Raspberry Pi
            cap = cv.VideoCapture(camera_index)

        if not cap.isOpened():
            print(f"[Camera] ╪º┘ä┘â╪º┘à┘è╪▒╪º {camera_index} ┘ä┘à ╪¬┘ü╪¬╪¡╪î ┘å╪¼╪▒╪¿ ╪º┘ä┘â╪º┘à┘è╪▒╪º ╪º┘ä╪¬╪º┘ä┘è╪⌐...")
            camera_index = 1
            cap = cv.VideoCapture(camera_index)
            
        if not cap.isOpened():
            print("[Camera] ╪«╪╖╪ú: ┘ä╪º ┘è┘à┘â┘å ╪º┘ä╪╣╪½┘ê╪▒ ╪╣┘ä┘ë ╪ú┘è ┘â╪º┘à┘è╪▒╪º!")
            return
        # ┘é╪▒╪º╪í╪º╪¬ ╪¬╪¼╪▒┘è╪¿┘è╪⌐ ┘ä┘ä╪Ñ╪¡┘à╪º╪í
        for _ in range(5):
            cap.read()

        hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        classifier = KeyPointClassifier()
        with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
            labels = [row[0] for row in csv.reader(f)]

        print("[Camera] ╪º┘ä┘â╪º┘à┘è╪▒╪º ╪¬╪╣┘à┘ä ╪¿┘å╪¼╪º╪¡ Γ£ô")

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
                    # ╪▒╪│┘à ╪«╪╖┘ê╪╖ ╪º┘ä╪¬╪¬╪¿╪╣ (Skeleton) ┘ä╪▒╪ñ┘è╪¬┘ç╪º ┘ü┘è ╪º┘ä┘à╪¬╪╡┘ü╪¡ ┘è╪¬┘à ┘è╪»┘ê┘è╪º┘ï ┘ü┘è ╪º┘ä╪ú╪│┘ü┘ä ┘ä╪╢┘à╪º┘å ╪º┘ä┘å╪╕╪º┘ü╪⌐ ╪¿╪»┘ê┘å ┘å┘é╪º╪╖
                    
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

                    # ╪▒╪│┘à ╪º┘ä┘à╪▒╪¿╪╣ ╪º┘ä┘à╪¡┘è╪╖ (Bounding Box) ╪¿╪º┘ä┘ä┘ê┘å ╪º┘ä╪ú╪│┘ê╪»
                    x_min, y_min = min([p[0] for p in landmark_list]), min([p[1] for p in landmark_list])
                    x_max, y_max = max([p[0] for p in landmark_list]), max([p[1] for p in landmark_list])
                    cv.rectangle(frame, (x_min - 10, y_min - 10), (x_max + 10, y_max + 10), (0, 0, 0), 1)

                    # ╪¬╪ú╪½┘è╪▒ ╪º┘ä┘ê┘à┘è╪╢ ┘à┘å ╪º┘ä╪»╪º╪«┘ä (Flash)
                    if state.blink_counter > 0:
                        overlay = frame.copy()
                        cv.rectangle(overlay, (x_min - 10, y_min - 10), (x_max + 10, y_max + 10), (255, 255, 255), -1)
                        cv.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
                        state.blink_counter -= 1

                    # ╪▒╪│┘à ╪º┘ä╪«╪╖┘ê╪╖ (White Lines)
                    for i, j in [(2,3),(3,4),(5,6),(6,7),(7,8),(9,10),(10,11),(11,12),(13,14),(14,15),(15,16),(17,18),(18,19),(19,20),(0,1),(1,2),(2,5),(5,9),(9,13),(13,17),(17,0)]:
                        cv.line(frame, tuple(landmark_list[i]), tuple(landmark_list[j]), (255, 255, 255), 2)

                    # ╪▒╪│┘à ╪º┘ä┘å┘é╪º╪╖ (White Circles)
                    for index, point in enumerate(landmark_list):
                        radius = 6 if index in [4, 8, 12, 16, 20] else 3
                        cv.circle(frame, tuple(point), radius, (255, 255, 255), -1)
                        cv.circle(frame, tuple(point), radius, (0, 0, 0), 1) # ╪Ñ╪╖╪º╪▒ ╪ú╪│┘ê╪» ╪▒┘é┘è┘é ┘ä┘ä┘å┘é╪╖╪⌐ ┘ä╪¬┘à┘è┘è╪▓┘ç╪º

            with state.lock:
                state.detected_char = char_found
                
                if char_found == state.last_stable_char and char_found != "":
                    state.char_counter += 1
                else:
                    state.char_counter = 0
                state.last_stable_char = char_found

                if state.char_counter == 18:
                    if char_found == "┘à╪│╪º┘ü╪⌐": state.word_buffer += " "
                    elif char_found == "╪¡╪░┘ü": state.word_buffer = state.word_buffer[:-1]
                    else: state.word_buffer += char_found
                    state.suggestions = get_conversational_ai(state.word_buffer)
                    state.char_counter = 0
                    state.blink_counter = 3 # ┘à╪»╪⌐ ╪º┘ä┘ê┘à┘è╪╢ (3 ╪Ñ╪╖╪º╪▒╪º╪¬)

            _, buffer = cv.imencode('.jpg', frame)
            state.current_frame = buffer.tobytes()

        cap.release()
        print("[Camera] ╪¬┘à ╪Ñ┘è┘é╪º┘ü ╪º┘ä┘â╪º┘à┘è╪▒╪º.")
    except Exception as e:
        print(f"[Camera] ╪«╪╖╪ú ┘ü┘è ╪º┘ä┘Ç detection thread: {e}")
        import traceback; traceback.print_exc()

# --- ┘à╪│╪º╪▒╪º╪¬ Flask ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/snapshot')
def snapshot():
    """╪Ñ╪▒╪¼╪º╪╣ ╪Ñ╪╖╪º╪▒ ┘ê╪º╪¡╪» ┘à┘å ╪º┘ä┘â╪º┘à┘è╪▒╪º ┘â╪╡┘ê╪▒╪⌐ JPEG"""
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
    """╪¡╪░┘ü ╪ó╪«╪▒ ╪¡╪▒┘ü (Backspace)"""
    with state.lock:
        state.word_buffer = state.word_buffer[:-1]
        state.suggestions = []
    return "OK"

@app.route('/clear_all', methods=['POST'])
def clear_all():
    """┘à╪│╪¡ ┘â┘ä ╪º┘ä╪¼┘à┘ä╪⌐"""
    with state.lock:
        state.word_buffer = ""
        state.suggestions = []
    return "OK"

@app.route('/add_space', methods=['POST'])
def add_space():
    """╪Ñ╪╢╪º┘ü╪⌐ ┘à╪│╪º┘ü╪⌐"""
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
        # ┘è┘à┘â┘å ╪Ñ╪╢╪º┘ü╪⌐ ┘à┘å╪╖┘é ┘ä╪¡┘ü╪╕ ╪º┘ä╪¼┘à┘ä╪⌐ ╪ú┘ê ╪Ñ╪▒╪│╪º┘ä┘ç╪º ┘ä┘à┘â╪º┘å ╪ó╪«╪▒
        state.word_buffer += ". "
    return "OK"

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """╪Ñ┘è┘é╪º┘ü ╪º┘ä╪│┘è╪▒┘ü╪▒ ┘à┘å ╪º┘ä┘ê╪º╪¼┘ç╪⌐"""
    state.is_running = False
    os._exit(0)
    return "Shutting down..."

if __name__ == '__main__':
    threading.Thread(target=detection_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
