# Arabic Sign Language Translation App

An advanced AI-powered application designed to translate Arabic Sign Language hand gestures into spoken voice and smart text suggestions in real-time. It aims to bridge the communication gap for the deaf and hard-of-hearing community.

---

## 🚀 Key Features

*   **Real-time & Stable Recognition:** Powered by MediaPipe for precise hand tracking, utilizing "Stability Logic" to ensure accurate character input without redundant repetition.
*   **Full Arabic Support:** Supports all Arabic alphabet characters, along with special gestures for Space and Backspace.
*   **Smart Prediction Engine:** A hybrid system that suggests words based on a local dictionary (`arabic_conversation.json`) and cloud-based intelligent queries.
*   **Text-to-Speech (TTS):** Converts translated text into natural-sounding voices (like "Hamed" or "Zariyah") using Microsoft's Neural Edge-TTS technology.
*   **Modern Web Interface:** Sleek "Glassmorphism" UI that is responsive, elegant, and user-friendly.
*   **Cross-Platform:** Runs as a Flask Web App or a direct Desktop Application (OpenCV).

---

## 🛠️ Tech Stack

*   **Language:** Python 3.8+
*   **Computer Vision:** OpenCV & MediaPipe
*   **AI Model:** TensorFlow Lite (MLP Classifier)
*   **Web Framework:** Flask, JavaScript, HTML5/CSS3
*   **Audio Engine:** Edge-TTS & Pygame

---

## 📦 Installation

1. Download or clone this repository to your machine.
2. Install the required dependencies using the following command:
```bash
pip install opencv-python mediapipe numpy flask edge-tts pygame requests arabic-reshaper python-bidi Pillow tensorflow
```

---

## 💻 How to Run

### 1️⃣ Web Version (Recommended)
Offers the best user experience with a polished UI:
```bash
python web_app.py
```
Once running, open your browser and go to: `http://localhost:5000`

### 2️⃣ Desktop Version
Best for quick testing or development:
```bash
python app.py
```

---

## ⌨️ Controls & Shortcuts

| Action | Web Version | Desktop Version |
| :--- | :--- | :--- |
| **Voice Playback** | "Speak" Button | Press **S** key |
| **Clear All** | "Finish Sentence" Button | Press **N** key |
| **Delete Character** | "Clear" Button | Press **Backspace** |
| **Add Space** | "Space" Gesture | Press **Space** bar |
| **Select Suggestion**| Click on Word | Press Keys **1-4** |
| **Exit App** | Close Terminal | Press **ESC** key |

---

## 🎯 Model Training & Development

The project is designed to be extensible. You can add new signs by:
1. Collecting data using `app.py` in "Logging Mode".
2. Training the model using the `keypoint_classification.ipynb` notebook.
3. Updating the label mapping in `model/keypoint_classifier/keypoint_classifier_label.csv`.

---

## 📜 License
This project is licensed under the Apache v2 License.

---
**Thank you for using this app!** We hope this project helps in making the world a more connected place.
