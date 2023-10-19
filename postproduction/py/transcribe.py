import numpy as np
import torch
import pandas as pd
import whisper

from operate_filename import determine_episode_type_and_number


class WhisperAPI:
    def __init__(self, model_name, language, verbose=True):
        self.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.language = language
        self.model = self._load_model(model_name, self.DEVICE)
        self.verbose = verbose

    def _load_model(self, model_name, device):
        model = whisper.load_model(model_name, device)
        print(
            f"Model is {'multilingual' if model.is_multilingual else 'English-only'} "
            f"and has {sum(np.prod(p.shape) for p in model.parameters()):,} parameters."
        )
        return model

    def _make_request(self, audio_file_path):
        return self.model.transcribe(
            audio_file_path,
            language=self.language,
            task="transcribe",
            verbose=self.verbose,
        )

    def make_df(self, transcription):
        return pd.DataFrame(transcription["segments"])[["id", "start", "end", "text"]]

    def transcribe(self, audio_file_path):
        return self._make_request(audio_file_path)


if __name__ == "__main__":
    import sys
    import time
    from IOManager import IOManager

    episode_type, episode_number = determine_episode_type_and_number(sys.argv[1])

    whisper_api = WhisperAPI("large-v2", "ja", verbose=True)
    audio_file_path = f"../episodes/{episode_type}/{episode_number}.mp3"
    csv_file_path = f"../csv/{episode_type}/{episode_number}.csv"

    t = time.time()
    transcription = whisper_api.transcribe(audio_file_path)
    print("time: ", time.time() - t)

    df = whisper_api.make_df(transcription)
    IOManager.save_df_to_csv(df, csv_file_path)
