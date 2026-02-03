import os
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

client = OpenAI(api_key=API_KEY)


def text_to_speech_file(text: str, folder: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(base_dir, "user_uploads", folder)
    save_file_path = os.path.join(save_dir, "audio.mp3")

    os.makedirs(save_dir, exist_ok=True)

    print(f"[TTS] Saving audio to: {save_file_path}")

    audio = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    with open(save_file_path, "wb") as f:
        f.write(audio.read())

    print(f"[TTS] ✅ Audio saved")
    return save_file_path

