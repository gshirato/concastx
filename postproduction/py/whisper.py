from dotenv import load_dotenv
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class WhisperAPI:
    def __init__(self, language):
        self.language = language

    def _make_request(self, audio_file_path):
        with open(audio_file_path, "rb") as audio_file:
            return openai.Audio.transcribe("whisper-1", audio_file)

    def transcribe(self, audio_file_path):
        return self._make_request(audio_file_path)

    def translate_and_transcribe(self, audio_file_path):
        return self._make_request(audio_file_path)


if __name__ == "__main__":
    whisper_api = WhisperAPI("ja")

    audio_file_path = "../episodes/concast/test.mp3"

    transcription = whisper_api.transcribe(audio_file_path)
    print("Transcription:", transcription)
