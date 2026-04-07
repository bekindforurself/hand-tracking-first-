import mediapipe as mp
print(dir(mp))
try:
    print(mp.solutions.hands)
except Exception as e:
    print(e)
