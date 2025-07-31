import os
import sqlite3
import sounddevice as sd
from scipy.io.wavfile import write

DB_PATH = "users.db"
VOICE_DIR = "voices"
SAMPLE_RATE = 16000
DURATION = 3  # seconds

os.makedirs(VOICE_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        voice_path TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

def enroll_user(name):
    voice_path = os.path.join(VOICE_DIR, f"{name}.wav")

    print(f"🔴 Recording for {name}. Please speak clearly in 5 seconds...")
    sd.sleep(5000)

    print("🎙️ Recording now...")
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    write(voice_path, SAMPLE_RATE, recording)
    print(f"✅ Saved voice to {voice_path}")

    # Store in DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, voice_path) VALUES (?, ?)", (name, voice_path))
        conn.commit()
        print("✅ User enrolled successfully.")
    except sqlite3.IntegrityError:
        print("⚠️ That user already exists.")
    conn.close()

if __name__ == "__main__":
    init_db()
    user_name = input("Enter your name for enrollment: ").strip().lower()
    enroll_user(user_name)
