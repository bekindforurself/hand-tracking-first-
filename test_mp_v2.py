try:
    import mediapipe.solutions.hands as mp_hands
    print("Success: import mediapipe.solutions.hands")
    print(dir(mp_hands))
except Exception as e:
    print(f"Error: {e}")
