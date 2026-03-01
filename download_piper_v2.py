import urllib.request
import os

os.makedirs('model/tts', exist_ok=True)

urls = {
    'model/tts/arabic_female.onnx': 'https://huggingface.co/vadimbelsky/arabic-emirati-female-piper/resolve/main/arabic-emirati-female-model.onnx',
    'model/tts/arabic_female.onnx.json': 'https://huggingface.co/vadimbelsky/arabic-emirati-female-piper/resolve/main/arabic-emirati-female-model.onnx.json'
}

for path, url in urls.items():
    if not os.path.exists(path):
        print(f"Downloading {url} to {path}...")
        urllib.request.urlretrieve(url, path)
        print(f"Finished {path}")
    else:
        print(f"{path} already exists.")
