import os
import time
import pygame
import threading

def speak_arabic_offline(text, piper_voice, engine):
    if not text.strip(): return
    
    def _run():
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            if piper_voice:
                temp_wav = f"speech_{int(time.time())}.wav"
                with open(temp_wav, "wb") as f:
                    piper_voice.synthesize(text, f, length_scale=1.2)
                
                if os.path.exists(temp_wav):
                    pygame.mixer.music.load(temp_wav)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    pygame.mixer.music.unload()
                    try: os.remove(temp_wav)
                    except: pass
                return
            
            # التراجع للنظام العادي
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    threading.Thread(target=_run, daemon=True).start()
