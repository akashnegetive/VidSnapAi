import os
import time
import subprocess
from PIL import Image
from text_to_audio import text_to_speech_file

Image.MAX_IMAGE_PIXELS = 20000000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "user_uploads")
DONE_FILE = os.path.join(BASE_DIR, "done.txt")

print("=== GENERATE_PROCESS LOADED ===")
print("BASE_DIR =", BASE_DIR)
print("UPLOADS_DIR =", UPLOADS_DIR)
print("DONE_FILE =", DONE_FILE)



# -----------------------------
# TEXT → AUDIO
# -----------------------------
def text_to_audio(folder):

    print("\n[TTS] start for folder:", folder)

    desc = os.path.join(UPLOADS_DIR, folder, "desc.txt")
    audio = os.path.join(UPLOADS_DIR, folder, "audio.mp3")

    print("[TTS] desc path:", desc)
    print("[TTS] audio path:", audio)

    if os.path.exists(audio):
        print("[TTS] audio exists size =", os.path.getsize(audio))

    if os.path.exists(audio) and os.path.getsize(audio) > 1000:
        print("[TTS] audio already exists — skip")
        return True

    if not os.path.exists(desc):
        print("[TTS] ❌ desc missing")
        return False

    text = open(desc, "r", encoding="utf-8").read().strip()
    print("[TTS] text length:", len(text))

    if not text:
        print("[TTS] ❌ empty text")
        return False

    print("[TTS] calling TTS engine...")

    try:
        text_to_speech_file(text, folder)
    except Exception as e:
        print("[TTS ERROR]", e)
        return False

    print("[TTS] waiting for audio write...")

    for i in range(20):
        if os.path.exists(audio):
            print("[TTS] audio detected size =", os.path.getsize(audio))
            if os.path.getsize(audio) > 1000:
                print("[TTS] ✅ audio ready")
                return True
        time.sleep(0.3)

    print("[TTS] ❌ audio not ready after wait")
    return False



# -----------------------------
# REEL CREATION
# -----------------------------
def create_reel(folder):

    print("\n[REEL] start for folder:", folder)

    input_txt = os.path.join(UPLOADS_DIR, folder, "input.txt")
    audio = os.path.join(UPLOADS_DIR, folder, "audio.mp3")
    output = os.path.join(BASE_DIR, "static", "reels", f"{folder}.mp4")

    print("[REEL] input_txt exists:", os.path.exists(input_txt))
    print("[REEL] audio exists:", os.path.exists(audio))
    print("[REEL] output path:", output)

    if not os.path.exists(input_txt):
        print("[REEL] ❌ input.txt missing")
        return False

    if not os.path.exists(audio):
        print("[REEL] ❌ audio missing")
        return False

    os.makedirs(os.path.dirname(output), exist_ok=True)

    cmd = [
    "ffmpeg",
    "-y",
    "-loglevel", "error",
    "-f", "concat",
    "-safe", "0",
    "-i", input_txt,
    "-i", audio,
    "-vf",
    "scale=720:1280:force_original_aspect_ratio=decrease,"
    "pad=720:1280:(ow-iw)/2:(oh-ih)/2:black,"
    "format=yuv420p",
    "-preset", "ultrafast",   # ⭐ KEY FIX
    "-crf", "28",             # ⭐ KEY FIX
    "-c:v", "libx264",
    "-c:a", "aac",
    "-shortest",
    output
    ]


    print("[REEL] running ffmpeg...")
    print("[REEL CMD]", " ".join(cmd))

    try:
        r = subprocess.run(cmd, capture_output=True, text=True)

        print("[REEL] return code:", r.returncode)

        if r.stderr:
            print("[FFMPEG STDERR]", r.stderr)

        if r.returncode != 0:
            print("[REEL] ❌ ffmpeg failed")
            return False

    except Exception as e:
        print("[REEL EXCEPTION]", e)
        return False

    print("[REEL] ✅ video created:", output)
    return True




# -----------------------------
# WORKER LOOP
# -----------------------------
def run_worker_loop():

    print("=== WORKER LOOP STARTED ===")

    while True:
        try:
            print("\n=== WORKER HEARTBEAT ===")

            os.makedirs(UPLOADS_DIR, exist_ok=True)

            if not os.path.exists(DONE_FILE):
                open(DONE_FILE, "a").close()

            done = set(open(DONE_FILE).read().split())
            folders = os.listdir(UPLOADS_DIR)

            print("SCAN PATH:", UPLOADS_DIR)
            print("FOLDERS:", folders)
            print("DONE:", done)

            for folder in folders:

                print("\n-- checking:", folder)

                if folder.startswith("."):
                    print("skip hidden")
                    continue

                full_path = os.path.join(UPLOADS_DIR, folder)

                if not os.path.isdir(full_path):
                    print("skip not dir")
                    continue

                if folder in done:
                    print("skip done")
                    continue

                print(">>> PROCESSING JOB:", folder)

                if not text_to_audio(folder):
                    print(">>> TTS failed — will retry later")
                    continue

               
                with open(DONE_FILE, "a") as f:
                    f.write(folder + "\n")

                create_reel(folder)

                print(">>> JOB COMPLETED:", folder)

        except Exception as e:
            print("[WORKER LOOP ERROR]", e)

        time.sleep(5)










