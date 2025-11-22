import os
import time
import subprocess
from text_to_audio import text_to_speech_file

def text_to_audio(folder):
    """Reads desc.txt and generates an audio.mp3 in the same folder."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    desc_path = os.path.join(base_dir, "user_uploads", folder, "desc.txt")

    print(f"[PROCESS] Reading description from: {desc_path}")
    if not os.path.exists(desc_path):
        print(f"[ERROR] desc.txt not found for {folder}")
        return

    with open(desc_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print(f"[WARNING] Empty desc.txt for {folder}, skipping TTS.")
        return

    text_to_speech_file(text, folder)


def create_reel(folder):
    """Combines images/videos and audio.mp3 into a single output reel using ffmpeg."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_txt = os.path.join(base_dir, "user_uploads", folder, "input.txt")
    audio_path = os.path.join(base_dir, "user_uploads", folder, "audio.mp3")
    output_path = os.path.join(base_dir, "static", "reels", f"{folder}.mp4")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(audio_path):
        print(f"[ERROR] audio.mp3 not found for {folder}. Skipping reel creation.")
        return

    command = (
        f'ffmpeg -f concat -safe 0 -i "{input_txt}" -i "{audio_path}" '
        f'-vf "scale=1080:1920:force_original_aspect_ratio=decrease,'
        f'pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" '
        f'-c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p "{output_path}"'
    )

    print(f"[REEL] Running FFmpeg command for {folder}...")
    subprocess.run(command, shell=True, check=True)
    print(f"[REEL] ✅ Reel created successfully: {output_path}")


if __name__ == "__main__":
    while True:
        print("\n[QUEUE] Checking for new folders...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        done_path = os.path.join(base_dir, "done.txt")
        uploads_path = os.path.join(base_dir, "user_uploads")

        # Create done.txt if missing
        if not os.path.exists(done_path):
            open(done_path, "a").close()

        with open(done_path, "r") as f:
            done_folders = [line.strip() for line in f if line.strip()]

        folders = os.listdir(uploads_path)

        for folder in folders:
            if folder not in done_folders:
                print(f"[QUEUE] Processing folder: {folder}")
                try:
                    text_to_audio(folder)
                    create_reel(folder)
                    with open(done_path, "a") as f:
                        f.write(folder + "\n")
                except Exception as e:
                    print(f"[ERROR] Failed to process {folder}: {e}")

        time.sleep(4)
