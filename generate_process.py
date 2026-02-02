import os
import time
import subprocess
from PIL import Image
from text_to_audio import text_to_speech_file


# -----------------------------
# IMAGE NORMALIZATION FIX
# -----------------------------
def normalize_images(folder):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "user_uploads", folder)

    for name in os.listdir(path):
        if name.lower().endswith((".jpg", ".jpeg", ".png")):
            full = os.path.join(path, name)
            try:
                img = Image.open(full).convert("RGB")
                img.save(full, "JPEG")
                print(f"[IMG] normalized {name}")
            except Exception as e:
                print(f"[IMG] skip bad image {name}: {e}")


# -----------------------------
# TEXT → AUDIO
# -----------------------------
def text_to_audio(folder):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    desc_path = os.path.join(base_dir, "user_uploads", folder, "desc.txt")

    print(f"[PROCESS] Reading description from: {desc_path}")

    if not os.path.exists(desc_path):
        print(f"[ERROR] desc.txt not found")
        return False

    with open(desc_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("[WARNING] Empty desc.txt")
        return False

    text_to_speech_file(text, folder)
    return True


# -----------------------------
# REEL CREATION
# -----------------------------
def create_reel(folder):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    input_txt = os.path.join(base_dir, "user_uploads", folder, "input.txt")
    audio_path = os.path.join(base_dir, "user_uploads", folder, "audio.mp3")
    output_path = os.path.join(base_dir, "static", "reels", f"{folder}.mp4")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(audio_path):
        print("[ERROR] audio.mp3 missing — skip reel")
        return

    command = [
        "ffmpeg",
        "-err_detect", "ignore_err",
        "-f", "concat",
        "-safe", "0",
        "-i", input_txt,
        "-i", audio_path,
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    print("[REEL] Running FFmpeg...")
    subprocess.run(command, check=True)
    print(f"[REEL] ✅ Created: {output_path}")


# -----------------------------
# QUEUE LOOP
# -----------------------------
if __name__ == "__main__":

    while True:
        print("\n[QUEUE] Checking folders...")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        done_path = os.path.join(base_dir, "done.txt")
        uploads_path = os.path.join(base_dir, "user_uploads")

        if not os.path.exists(done_path):
            open(done_path, "a").close()

        with open(done_path, "r") as f:
            done_folders = [x.strip() for x in f if x.strip()]

        for folder in os.listdir(uploads_path):

            if folder in done_folders:
                continue

            print(f"[QUEUE] Processing {folder}")

            try:
                ok = text_to_audio(folder)
                if not ok:
                    continue

                normalize_images(folder)   # ⭐ NEW FIX
                create_reel(folder)

                with open(done_path, "a") as f:
                    f.write(folder + "\n")

            except Exception as e:
                print(f"[ERROR] {folder}: {e}")

        time.sleep(4)
