import os
import wave
import sys
from piper.voice import PiperVoice

# مسار الموديلات
MODEL_PATH = "model/tts/arabic_female.onnx"
CONFIG_PATH = "model/tts/arabic_female.onnx.json"
OUTPUT_WAV = "test_output.wav"

if not os.path.exists(MODEL_PATH):
    print(f"Error: Model not found at {MODEL_PATH}")
    sys.exit(1)

text = "مرحبا بك في تطبيق لغة الإشارة"

try:
    print("Loading piper voice...")
    voice = PiperVoice.load(MODEL_PATH, config_path=CONFIG_PATH)
    
    print(f"Synthesizing text: {text}")
    with wave.open(OUTPUT_WAV, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    
    print(f"Success! Output saved to {OUTPUT_WAV}")
    
    # محاولة التشغيل للتأكد
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT_WAV)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass
    print("Playback finished.")

except Exception as e:
    print(f"Error: {e}")
