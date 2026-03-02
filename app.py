#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv, copy, argparse, itertools, os, requests, json, threading, pygame
from gtts import gTTS


from collections import Counter, deque
import cv2 as cv
import numpy as np
import mediapipe as mp
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import ImageFont, ImageDraw, Image
from utils import CvFpsCalc
from model import KeyPointClassifier

# --- محرك التنبؤ الذكي "سنابل" (Conversational AI - Offline First) ---
CONVERSATION_FILE = "arabic_conversation.json"
LOADED_DICT = {}
if os.path.exists(CONVERSATION_FILE):
    try:
        with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
            LOADED_DICT = json.load(f)
    except: pass
    
# --- إعدادات الصوت (TTS - Google) ---
pygame.mixer.init()

def speak_text(text):
    if not text.strip(): return
    def run():
        try:
            tts = gTTS(text=text, lang='ar')
            temp_file = "temp_speech.mp3"
            tts.save(temp_file)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.music.unload() # تحرير الملف للحذف
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Error playing sound: {e}")
            
    threading.Thread(target=run).start()



# قائمة الكلمات الشائعة للتكملة التلقائية (Autocomplete)
COMMON_WORDS = ["أنا", "أريد", "يذهب", "اذهب", "نذهب", "تذهب", "أين", "أحب", "أحتاج", "كيف", "مرحبا", "شكرا", "السلام", "هل", "في", "إلى", "من", "رايح", "بدي", "وين", "شو", "لو", "ان", "شاء", "الله", "يا", "اخي", "امي", "ابي", "تعبان", "جائع", "مريض", "بخير", "دكتور", "مستشفى", "حمام", "ماء", "اكل", "نوم"]

def normalize(text):
    """تطهير النص لضمان المطابقة"""
    return text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي").strip()

def get_conversational_ai(text):
    """محرك هجين: محلي (حواري) + سحابي (ذكي)"""
    raw_text = text.strip()
    if not raw_text: return []
    
    words = raw_text.split()
    last_word = words[-1]
    last_word_norm = normalize(last_word)
    
    # 1. التكملة التلقائية للكلمة الحالية (Autocomplete)
    # إذا كانت الكلمة لم تكتمل بعد (لا يوجد مسافة في النهاية)
    if not text.endswith(" "):
        completions = [w for w in COMMON_WORDS if normalize(w).startswith(last_word_norm)]
        if completions and len(completions[0]) > len(last_word):
            return completions[:4] # نعيد الكلمات المقترحة لتكملة الحالية

    # 2. التنبؤ بالكلمة التالية (Next Word Prediction)
    # البحث في القاموس الحواري المحلي
    for key, predictions in LOADED_DICT.items():
        if normalize(key) == last_word_norm:
            return predictions[:4]

    # 3. محرك جوجل المفلتر (للمات لم تتوفر محلياً)
    try:
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={raw_text}&hl=ar"
        resp = requests.get(url, timeout=0.8)
        if resp.status_code == 200:
            raw_cloud = json.loads(resp.text)[1]
            cloud_clean = []
            forbidden = ["اخبار", "طقس", "مباراة", "فيلم", "سعر", "يوتيوب"]
            for s in raw_cloud:
                if any(f in s for f in forbidden): continue # استبعاد الاخبار والافلام
                
                # استخراج التكملة الذكية بناءً على موضع الكلمات
                q_words = raw_text.split()
                s_words = s.split()
                idx = len(q_words) if text.endswith(" ") else len(q_words) - 1
                s_sug = " ".join(s_words[idx:]) if len(s_words) > idx else s
                
                if s_sug and len(s_sug.split()) <= 2:
                    cloud_clean.append(s_sug)
            return cloud_clean[:4]
    except: pass

    return []

FONT_PATH = os.path.join('font', 'trado.ttf') 
word_buffer = ""
last_stable_char = ""
char_counter = 0
suggestions = []

def draw_arabic_text(image, text, position, font, color=(255, 255, 255)):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)
    draw.text(position, bidi_text, font=font, fill=color)
    return np.array(img_pil)

def update_sugs(text):
    global suggestions
    suggestions = get_conversational_ai(text)

def main():
    global word_buffer, last_stable_char, char_counter, suggestions
    cap = cv.VideoCapture(0)
    hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
    classifier = KeyPointClassifier()
    with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
        labels = [row[0] for row in csv.reader(f)]
    
    font = ImageFont.truetype(FONT_PATH, 32) if os.path.exists(FONT_PATH) else ImageFont.load_default()
    font_small = ImageFont.truetype(FONT_PATH, 24) if os.path.exists(FONT_PATH) else ImageFont.load_default()

    while True:
        key = cv.waitKey(10)
        if key == 27: break # ESC to exit

        if 49 <= key <= 52: # 1-4
            idx = key - 49
            if idx < len(suggestions):
                sug = suggestions[idx]
                # هل الاقتراح هو تكملة لنفس الكلمة ام كلمة جديدة؟
                words = word_buffer.strip().split()
                if not word_buffer.endswith(" ") and words:
                    words[-1] = sug
                    word_buffer = " ".join(words) + " "
                else:
                    word_buffer = word_buffer.strip() + " " + sug + " "
                suggestions = []

        if key == ord('n'): word_buffer = ""; suggestions = []
        if key == 8: word_buffer = word_buffer[:-1]; suggestions = []
        if key == 32: word_buffer += " "; threading.Thread(target=update_sugs, args=(word_buffer,)).start()
        if key == ord('s'): speak_text(word_buffer) # حرف S للنطق


        ret, image = cap.read()
        if not ret: break
        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image)
        results = hands.process(cv.cvtColor(image, cv.COLOR_BGR2RGB))

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
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
                char = labels[char_id]

                if char == last_stable_char and char != "": char_counter += 1
                else: char_counter = 0
                last_stable_char = char

                if char_counter == 18:
                    if char == "مسافة": word_buffer += " "
                    elif char == "حذف": word_buffer = word_buffer[:-1]; suggestions = []
                    else: word_buffer += char
                    
                    if word_buffer.strip():
                        threading.Thread(target=update_sugs, args=(word_buffer,)).start()
                    char_counter = 0

                for i, j in [(2,3),(3,4),(5,6),(6,7),(7,8),(9,10),(10,11),(11,12),(13,14),(14,15),(15,16),(17,18),(18,19),(19,20),(0,1),(1,2),(2,5),(5,9),(9,13),(13,17),(17,0)]:
                    cv.line(debug_image, tuple(landmark_list[i]), tuple(landmark_list[j]), (255, 255, 255), 2)
                for p in landmark_list:
                    cv.circle(debug_image, tuple(p), 5, (0, 255, 0), -1)

        # واجهة التنبؤ (Gboard Style)
        if suggestions:
            cv.rectangle(debug_image, (0, 355), (640, 420), (15, 15, 15), -1)
            for i, sug in enumerate(suggestions[:4]):
                x_pos = 10 + (i * 155)
                cv.rectangle(debug_image, (x_pos, 362), (x_pos+150, 412), (0, 110, 0), -1)
                short_sug = sug if len(sug) < 14 else sug[:11] + ".."
                debug_image = draw_arabic_text(debug_image, f"{i+1}:{short_sug}", (x_pos + 10, 372), font_small)

        cv.rectangle(debug_image, (0, 420), (640, 480), (0, 0, 0), -1)
        debug_image = draw_arabic_text(debug_image, "الجملة (ذكاء اصطناعي): " + word_buffer, (10, 425), font)
        debug_image = draw_arabic_text(debug_image, "تنبؤات حوارية (1-4 للاختيار) | مفتاح S للنطق | N للمسح", (10, 458), font_small, color=(160, 160, 160))

        
        cv.imshow('Smart Conversational ASL', debug_image)

    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
