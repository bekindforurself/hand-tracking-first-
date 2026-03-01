import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("--- القائمة الكاملة للأصوات المثبتة في جهازك ---")
for index, voice in enumerate(voices):
    print(f"[{index}] الاسم: {voice.name}")
    print(f"    اللغة: {voice.languages}")
    print(f"    المعرف: {voice.id}")
    print("-" * 30)

if len(voices) == 0:
    print("تحذير: لم يتم العثور على أي أصوات مثبتة.")
