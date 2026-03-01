try:
    from piper.voice import PiperVoice
    print("Piper imported successfully")
except ImportError as e:
    print(f"Error importing Piper: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
