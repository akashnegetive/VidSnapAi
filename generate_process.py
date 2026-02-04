import os
import time
import subprocess
from PIL import Image
from text_to_audio import text_to_speech_file

Image.MAX_IMAGE_PIXELS = 20000000

# -----------------------------
# IMAGE NORMALIZATION
# -----------------------------
# def normalize_images(folder):
#     base = os.path.dirname(os.path.abspath(__file__))
#     path = os.path.join(base, "user_uploads", folder)

#     for name in os.listdir(path):
#         if name.lower().endswith((".jpg",".jpeg",".png")):
#             full = os.path.join(path, name)
#             try:
#                 Image.open(full).convert("RGB").save(full, "JPEG")
#                 print("[IMG] normalized", name)
#             except Exception as e:
#                 print("[IMG] skip", name, e)


# -----------------------------
# TEXT → AUDIO
# -----------------------------
def text_to_audio(folder):

    base = os.path.dirname(os.path.abspath(__file__))
    desc = os.path.join(base,"user_uploads",folder,"desc.txt")
    audio = os.path.join(base,"user_uploads",folder,"audio.mp3")

    # ✅ skip if audio already exists
    if os.path.exists(audio) and os.path.getsize(audio) > 1000:
        print("[TTS] audio already exists — skip")
        return True

    if not os.path.exists(desc):
        print("[TTS] desc missing")
        return False

    text = open(desc,"r",encoding="utf-8").read().strip()
    if not text:
        print("[TTS] empty text")
        return False

    text_to_speech_file(text, folder)

    # ⭐ WAIT FOR AUDIO WRITE (race fix)
    audio = os.path.join(base,"user_uploads",folder,"audio.mp3")

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

    base = os.path.dirname(os.path.abspath(__file__))

    input_txt = os.path.join(base,"user_uploads",folder,"input.txt")
    audio = os.path.join(base,"user_uploads",folder,"audio.mp3")
    output = os.path.join(base,"static","reels",f"{folder}.mp4")

    os.makedirs(os.path.dirname(output), exist_ok=True)

    if not os.path.exists(audio):
        print("[REEL] audio missing")
        return

    cmd = [
        "ffmpeg",
        "-y",
        "-err_detect","ignore_err",
        "-threads 1",
        "-f","concat","-safe","0",
        "-i", input_txt,
        "-i", audio,
       "-vf",
        "scale=720:1280:force_original_aspect_ratio=decrease,"
        "pad=720:1280:(ow-iw)/2:(oh-ih)/2:black,"
        "format=yuv420p",
        "-c:v","libx264",
        "-c:a","aac",
        "-shortest",
        "-r","30",
        output
    ]

    print("[REEL] ffmpeg start")

    r = subprocess.run(cmd, capture_output=True, text=True)

    print("[FFMPEG STDERR]\n", r.stderr)

    if r.returncode != 0:
        print("[REEL] ffmpeg failed")
        return

    print("[REEL] created", output)


# -----------------------------
# WORKER LOOP (THREAD MODE)
# -----------------------------
def run_worker_loop():

    while True:

        base = os.path.dirname(os.path.abspath(__file__))
        done_file = os.path.join(base,"done.txt")
        uploads = os.path.join(base,"user_uploads")

        if not os.path.exists(done_file):
            open(done_file,"a").close()

        done = set(open(done_file).read().split())
        print("UPLOAD PATH:", uploads)
        print("UPLOAD CONTENT:", os.listdir(uploads))


        for folder in os.listdir(uploads):

            # if folder in done:
            #     continue

            print("[QUEUE]", folder)
            print("FOLDER FILES:", os.listdir(os.path.join(uploads, folder)))

            try:
                if not text_to_audio(folder):
                    continue

                #normalize_images(folder)
                create_reel(folder)

                with open(done_file,"a") as f:
                    f.write(folder+"\n")

            except Exception as e:
                print("[WORKER ERROR]", e)

        time.sleep(4)





