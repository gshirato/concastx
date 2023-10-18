import sys

from mutagen.id3 import ID3, CTOCFlags, TIT2, CTOC, CHAP
from mutagen.mp3 import MP3
import numpy as np
import pandas as pd

from typing import List, Tuple

from operate_filename import determine_episode_type_and_number


class AudioTagger:
    def __init__(self, episode_type: str, episode_number: str):
        self.episode_type = episode_type
        self.episode_number = episode_number
        self.audio = ID3(f"../episodes/{episode_type}/{episode_number}.mp3")

    @staticmethod
    def parse_timestr_milliseconds(timestr: str) -> int:
        time_list = [int(x) for x in timestr.split(".")[0].split(":")]

        if len(time_list) == 2:
            return (time_list[0] * 60 + time_list[1]) * 1000
        elif len(time_list) == 3:
            return (time_list[0] * 3600 + time_list[1] * 60 + time_list[2]) * 1000
        else:
            raise ValueError(f"Invalid time format: {timestr}")

    def get_time_data_from_csv(self) -> Tuple[List[str], List[str], List[str]]:
        df = pd.read_csv(
            f"markers/{self.episode_type}/{self.episode_number}.csv", sep="\t"
        )
        return df["Start"].tolist(), df["Name"].tolist(), df["Duration"].tolist()

    def add_tags(self):
        print(self.audio)

        start, title, duration = self.get_time_data_from_csv()

        start_seconds = np.array([self.parse_timestr_milliseconds(t) for t in start])
        duration_seconds = np.array(
            [self.parse_timestr_milliseconds(t) for t in duration]
        )
        end_seconds = start_seconds + duration_seconds

        child_elements = [f"chp{i}" for i in range(1, len(title) + 1)]

        self.audio.add(
            CTOC(
                element_id="toc",
                flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
                child_element_ids=child_elements,
            )
        )

        print("-" * 40)
        print("Start   End     Title")
        for elem, s, e, t in zip(child_elements, start_seconds, end_seconds, title):
            print(s, e, t)
            self.audio.add(
                CHAP(
                    element_id=elem,
                    start_time=s,
                    end_time=e,
                    sub_frames=[TIT2(text=[t])],
                )
            )
        print(self.audio)
        self.audio.save()


if __name__ == "__main__":
    episode_type, episode_number = determine_episode_type_and_number(sys.argv[1])

    tagger = AudioTagger(episode_type, episode_number)
    tagger.add_tags()
