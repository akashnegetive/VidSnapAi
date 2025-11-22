import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY

# Initialize ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def text_to_speech_file(text: str, folder: str) -> str:
    """
    Converts text to speech and saves it as audio.mp3 inside the user_uploads/<folder>.
    Returns the path to the saved file.
    """
    # Ensure consistent file paths regardless of where script is executed
    base_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(base_dir, "user_uploads", folder)
    save_file_path = os.path.join(save_dir, "audio.mp3")

    # Ensure the output folder exists
    os.makedirs(save_dir, exist_ok=True)

    print(f"[TTS] Saving audio to: {save_file_path}")
    print(f"[TTS] Current working directory: {os.getcwd()}")

    # Call the ElevenLabs API
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )

    # Write the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"[TTS] ✅ Audio file saved successfully: {save_file_path}")
    return save_file_path


# Debug test (uncomment for testing)
# text_to_speech_file("Hey Akash", "d8026807-bb46-11f0-997b-6c9466b788f0")
