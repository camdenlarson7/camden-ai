import sqlite3
import os
import sounddevice as sd
from scipy.io.wavfile import write
from speechbrain.inference import SpeakerRecognition

DB_PATH = "users.db"
SAMPLE_RATE = 16000
TEST_PATH = "test_speaker.wav"

def record_test_snippet(duration=2):
    print("🎤 Say the wake word (or speak)...")
    recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    write(TEST_PATH, SAMPLE_RATE, recording)

def verify_against_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, voice_path FROM users")
    users = c.fetchall()
    conn.close()

    model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec")

    best_score = 0
    best_match = None

    for name, path in users:
        score, prediction = model.verify_files(path, TEST_PATH)
        print(f"🧠 Comparing to {name}: score = {score:.3f}")
        if prediction and score > best_score:
            best_score = score
            best_match = name

    if best_match:
        print(f"✅ Matched speaker: {best_match} (score: {best_score:.3f})")
        return best_match
    else:
        print("❌ No matching speaker found.")
        return None

if __name__ == "__main__":
    record_test_snippet()
    verify_against_all_users()
