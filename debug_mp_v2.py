import mediapipe as mp
print(f"File: {mp.__file__}")
print(f"Dir contents: {dir(mp)}")
try:
    from mediapipe.python import solutions as solutions
    print("Imported from mediapipe.python.solutions successfully!")
except Exception as e:
    print(f"Failed to import from internal: {e}")
