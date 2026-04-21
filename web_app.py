import csv, copy, argparse, itertools, os, requests, json, threading, pygame, time, socket, cv2 as cv, numpy as np, mediapipe as mp, asyncio, edge_tts
from flask import Flask, render_template, Response, jsonify, request
import logging

from collections import Counter, deque
from model import KeyPointClassifier

# --- Hands Wrapper ---
from mediapipe.tasks.python import vision
from mediapipe import Image as MpImage, ImageFormat

class _HandLandmark:
    def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z
class _HandLandmarks:
    def __init__(self, lms): self.landmark = lms
class _HandsResult:
    def __init__(self, multi_hand_landmarks):
        self.multi_hand_landmarks = multi_hand_landmarks or []

class Hands:
    def __init__(self, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        base_options = mp.tasks.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence
        )
        self._detector = vision.HandLandmarker.create_from_options(options)
    def process(self, rgb_image):
        mp_image = MpImage(image_format=ImageFormat.SRGB, data=rgb_image)
        res = self._detector.detect(mp_image)
        if not res or not res.hand_landmarks: return _HandsResult(None)
        multi = []
        for lms in res.hand_landmarks:
            multi.append(_HandLandmarks([_HandLandmark(l.x, l.y, l.z) for l in lms]))
        return _HandsResult(multi)

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class GlobalState:
    def __init__(self):
        self.word_buffer = ""
        self.detected_char = ""
        self.suggestions = []
        self.last_stable_char = ""
        self.char_counter = 0
        self.stability_time = 0 
        self.lock = threading.Lock()
        self.is_running = True
        self.is_capturing = True 
        self.two_hand_mode = False
        self.record_label = -1 
        self.record_type = "single" 
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        _, buf = cv.imencode('.jpg', blank)
        self.current_frame = buf.tobytes()

state = GlobalState()
pygame.mixer.init()

def speak_text(text):
    if not text.strip(): return
    def run():
        try:
            VOICE = "ar-SA-ZariyahNeural"
            temp_file = f"temp_speech_{int(time.time())}.mp3"
            async def generate():
                communicate = edge_tts.Communicate(text, VOICE)
                await communicate.save(temp_file)
            asyncio.run(generate())
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): time.sleep(0.1)
            pygame.mixer.music.unload()
            if os.path.exists(temp_file): os.remove(temp_file)
        except: pass
    threading.Thread(target=run).start()

def logging_csv(number, landmark_list, filename='model/keypoint_classifier/keypoint.csv'):
    with open(filename, 'a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([number, *landmark_list])

def pre_process_landmarks(landmark_list, w=640, h=480):
    temp_landmark_list = copy.deepcopy(landmark_list)
    base_x, base_y = temp_landmark_list[0][0], temp_landmark_list[0][1]
    for i in range(len(temp_landmark_list)):
        temp_landmark_list[i][0] = temp_landmark_list[i][0] - base_x
        temp_landmark_list[i][1] = temp_landmark_list[i][1] - base_y
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))
    max_value = max(list(map(abs, temp_landmark_list)))
    def normalize_(n): return n / max_value if max_value != 0 else n
    temp_landmark_list = list(map(normalize_, temp_landmark_list))
    return temp_landmark_list

def detection_thread():
    global state
    try:
        is_windows = (os.name == 'nt')
        if is_windows:
            cap = cv.VideoCapture(0, cv.CAP_DSHOW)
            W, H = 640, 480
        else:
            cap = cv.VideoCapture(0)
            W, H = 320, 240
            
        cap.set(cv.CAP_PROP_FRAME_WIDTH, W)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, H)
        
        # تقليل عتبة الرصد (min_detection_confidence) إلى 0.4 لزيادة فرصة رصد اليدين المتقاربتين
        hands = Hands(max_num_hands=2, min_detection_confidence=0.4)
        classifier = KeyPointClassifier()
        num_classifier = None
        if os.path.exists('model/keypoint_classifier/keypoint_numbers_classifier.tflite'):
            num_classifier = KeyPointClassifier('model/keypoint_classifier/keypoint_numbers_classifier.tflite')
        
        with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
            labels = [row[0] for row in csv.reader(f)]
        num_labels = []
        if os.path.exists('model/keypoint_classifier/keypoint_numbers_label.csv'):
            with open('model/keypoint_classifier/keypoint_numbers_label.csv', encoding='utf-8-sig') as f:
                num_labels = [row[0] for row in csv.reader(f)]

        cooldown_until = 0
        frame_count = 0

        while state.is_running:
            ret, frame = cap.read()
            if not ret: continue
            frame = cv.flip(frame, 1)
            
            frame_count += 1
            char_found = ""

            if state.is_capturing:
                if is_windows or (frame_count % 3 == 0):
                    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    results = hands.process(rgb_frame)
                    
                    if results.multi_hand_landmarks:
                        num_hands = len(results.multi_hand_landmarks)
                        state.two_hand_mode = (num_hands == 2)
                        all_raw_hands_data = []

                        # رسم السكيلتون وحساب البيانات
                        hand_processed_count = 0
                        for hand_landmarks in results.multi_hand_landmarks:
                            landmark_list = []
                            for landmark in hand_landmarks.landmark:
                                landmark_list.append([min(int(landmark.x * W), W-1), min(int(landmark.y * H), H-1)])
                            
                            # رسم السكيلتون النقاط دائماً للتأكد من الرصد
                            for i, j in [(2,3),(3,4),(5,6),(6,7),(7,8),(9,10),(10,11),(11,12),(13,14),(14,15),(15,16),(17,18),(18,19),(19,20),(0,1),(1,2),(2,5),(5,9),(9,13),(13,17),(17,0)]:
                                cv.line(frame, tuple(landmark_list[i]), tuple(landmark_list[j]), (255, 255, 255), 2)
                            for idx in [4, 8, 12, 16, 20]:
                                cv.circle(frame, tuple(landmark_list[idx]), 4, (0, 165, 255), -1)

                            all_raw_hands_data.append(landmark_list)
                            hand_processed_count += 1

                        # منطق الفصل الصارم:
                        if num_hands == 2 and num_classifier and len(all_raw_hands_data) == 2:
                            # وضع الأرقام (تجاهل الحروف تماماً)
                            dual_pts = []
                            for h_pts in all_raw_hands_data:
                                dual_pts.extend(pre_process_landmarks(h_pts, W, H))
                            num_id = num_classifier(dual_pts)
                            if num_id < len(num_labels):
                                char_found = num_labels[num_id]
                        elif num_hands == 1:
                            # وضع الحروف (تجاهل الأرقام)
                            processed = pre_process_landmarks(all_raw_hands_data[0], W, H)
                            char_id = classifier(processed)
                            raw_char = labels[char_id] if char_id < len(labels) else ""
                            if raw_char == "أ": raw_char = "ا"
                            char_found = raw_char
                            landmark_out = processed
                    else:
                        state.two_hand_mode = False
                        char_found = ""
                else:
                    char_found = state.detected_char
            else:
                cv.putText(frame, "Capture Paused", (int(W/4), int(H/2)), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            with state.lock:
                state.detected_char = char_found
                if char_found == state.last_stable_char and char_found != "":
                    if state.stability_time == 0: state.stability_time = time.time()
                    if time.time() - state.stability_time >= 1.5 and time.time() > cooldown_until:
                        if char_found == "مسافة": state.word_buffer += " "
                        elif char_found == "حذف": state.word_buffer = state.word_buffer[:-1]
                        else: state.word_buffer += char_found
                        cooldown_until = time.time() + 2.0
                        state.stability_time = time.time()
                else: state.stability_time = 0
                state.last_stable_char = char_found

            _, buffer = cv.imencode('.jpg', frame)
            state.current_frame = buffer.tobytes()

    except Exception as e:
        print(f"[Debug] Error: {e}")
    finally:
        if cap: cap.release()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + state.current_frame + b'\r\n')
            time.sleep(0.03)
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_status')
def get_status():
    with state.lock:
        return jsonify({
            "sentence": state.word_buffer,
            "detected_char": state.detected_char,
            "suggestions": [],
            "two_hand_mode": state.two_hand_mode,
            "is_capturing": state.is_capturing
        })

@app.route('/toggle_capture', methods=['POST'])
def toggle_capture():
    with state.lock:
        state.is_capturing = not state.is_capturing
    return "OK"

@app.route('/record_now', methods=['POST'])
def record_now():
    label = request.args.get('label', type=int)
    rtype = request.args.get('type', default="single")
    if label is not None:
        with state.lock:
            state.record_label = label
            state.record_type = rtype
    return "OK"

@app.route('/speak', methods=['POST'])
def speak():
    speak_text(state.word_buffer)
    return "OK"

@app.route('/clear_all', methods=['POST'])
def clear_all():
    with state.lock:
        state.word_buffer = ""
    return "OK"

if __name__ == '__main__':
    threading.Thread(target=detection_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
