import mediapipe as mp
try:
    print(f"MediaPipe version: {mp.__version__}")
    print(f"Solutions: {mp.solutions}")
    print("Success!")
except AttributeError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"General Error: {e}")
