import urllib.request
import os

os.makedirs('model/tts', exist_ok=True)

urls = {
    'model/tts/ar_JO-naay-medium.onnx': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/naay/medium/ar_JO-naay-medium.onnx',
    'model/tts/ar_JO-naay-medium.onnx.json': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/naay/medium/ar_JO-naay-medium.onnx.json'
}

for path, url in urls.items():
    if not os.path.exists(path):
        print(f"Downloading {url} to {path}...")
        urllib.request.urlretrieve(url, path)
        print(f"Finished {path}")
    else:
        print(f"{path} already exists.")
