import os
import time
import subprocess
from PIL import Image
from text_to_audio import text_to_speech_file

Image.MAX_IMAGE_PIXELS = 20000000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "user_uploads")
DONE_FILE = os.path.join(BASE_DIR, "done.txt")


# -----------------------------
# TEXT → AUDIO
# -----------------------------
def text_to_audio(folder):

    desc = os.path.join(UPLOADS_DIR, folder, "desc.txt")
    audio = os.path.join(UPLOADS_DIR, folder, "audio.mp3")

    if os.path.exists(audio) and os.path.getsize(audio) > 1000:
        print("[TTS] audio already exists — skip")
        return True

    if not os.path.exists(desc):
        print("[TTS] desc missing")
        return False

    text = open(desc, "r", encoding="utf-8").read().strip()
    if not text:
        print("[TTS] empty text")
        return False

    try:
        text_to_speech_file(text, folder)
    except Exception as e:
        print("[TTS ERROR]", e)
        return False

    # wait for file write
    for _ in range(20):
        if os.path.exists(audio) and os.path.getsize(audio) > 1000:
            print("[TTS] audio ready")
            return True
        time.sleep(0.3)

    print("[TTS] audio not ready")
    return False


# -----------------------------
# REEL CREATION
# -----------------------------
def create_reel(folder):

    input_txt = os.path.join(UPLOADS_DIR, folder, "input.txt")
    audio = os.path.join(UPLOADS_DIR, folder, "audio.mp3")
    output = os.path.join(BASE_DIR, "static", "reels", f"{folder}.mp4")

    os.makedirs(os.path.dirname(output), exist_ok=True)

    if not os.path.exists(audio):
        print("[REEL] audio missing")
        return

    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel", "error",   # ✅ remove warning spam
        "-f", "concat",
        "-safe", "0",
        "-i", input_txt,
        "-i", audio,
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
        "format=yuv420p",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-r", "30",
        output
    ]

    print("[REEL] ffmpeg start")

    r = subprocess.run(cmd, capture_output=True, text=True)

    if r.returncode != 0:
        print("[FFMPEG ERROR]", r.stderr)
        return

    print("[REEL] created", output)


# -----------------------------
# WORKER LOOP
# -----------------------------
def run_worker_loop():

    print("=== WORKER LOOP STARTED ===")

    while True:
        try:

            os.makedirs(UPLOADS_DIR, exist_ok=True)

            if not os.path.exists(DONE_FILE):
                open(DONE_FILE, "a").close()

            done = set(open(DONE_FILE).read().split())
            folders = os.listdir(UPLOADS_DIR)

            print("WORKER SCAN FULL:", UPLOADS_DIR, folders)
            print("DONE LIST:", done)
            
            for folder in folders:

                if folder.startswith("."):
                    continue

                if folder in done:
                    continue

                print("=== PROCESSING:", folder)

                if not text_to_audio(folder):
                    continue

                create_reel(folder)

                with open(DONE_FILE, "a") as f:
                    f.write(folder + "\n")

                print("=== DONE:", folder)

        except Exception as e:
            print("[WORKER LOOP ERROR]", e)

        time.sleep(5)



