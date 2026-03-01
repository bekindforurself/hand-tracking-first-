import urllib.request
import os

os.makedirs('model/tts', exist_ok=True)

# سنستخدم صوت "كريم" (Kareem) - صوت رجل أردني هادئ وواضح بالفصحى (بديل للأنثى المتعثرة)
# أو سنحولها لصوت أنثى إذا وجدنا رابطاً مباشراً لصوت "ليلى" أو غيره.
urls = {
    'model/tts/arabic_male_v2.onnx': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx',
    'model/tts/arabic_male_v2.onnx.json': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx.json'
}

for path, url in urls.items():
    if not os.path.exists(path):
        print(f"Downloading {url} to {path}...")
        urllib.request.urlretrieve(url, path)
        print(f"Finished {path}")
    else:
        print(f"{path} already exists.")
