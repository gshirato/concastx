import sys

from mutagen.id3 import ID3, CTOCFlags, TIT2, CTOC, CHAP
from mutagen.mp3 import MP3
import numpy as np
import pandas as pd

from typing import List, Tuple

from operate_filename import determine_episode_name_and_number


class AudioTagger:
    def __init__(self, episode_name: str):
        self.episode_name = episode_name
        self.audio = ID3(f"../episodes/{episode_name}.mp3")

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
        df = pd.read_csv(f"markers/{self.episode_name}.csv", sep="\t")
        return df["Start"].tolist(), df["Name"].tolist(), df["Duration"].tolist()

    def add_tags(self):
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

        self.audio.save()


def parse_timestr_milliseconds(timestr):
    time_list_str = timestr.split(".")[0].split(":")
    time_list = list(map(int, time_list_str))
    if len(time_list) == 2:
        return (time_list[0] * 60 + time_list[1]) * 1000
    if len(time_list) == 3:
        return (time_list[0] * 3600 + time_list[1] * 60 + time_list[2]) * 1000
    raise ValueError(f"Invalid time format: {timestr}")


def get_time_data_from_csv(episode_name: str) -> Tuple[List[str], List[str], List[str]]:
    df = pd.read_csv(f"markers/{episode_name}.csv", sep="\t")
    return df["Start"].tolist(), df["Name"].tolist(), df["Duration"].tolist()


def add_tags(episode_name):
    audio = ID3(f"../episodes/{episode_name}.mp3")
    print("audio before edit")
    print(audio)

    start, title, duration = get_time_data_from_csv(episode_name)

    start_seconds = np.array([parse_timestr_milliseconds(t) for t in start])
    duration_seconds = np.array([parse_timestr_milliseconds(t) for t in duration])
    end_seconds = start_seconds + duration_seconds

    child_elements = [f"chp{i}" for i in range(1, len(title) + 1)]

    audio.add(
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
        audio.add(
            CHAP(element_id=elem, start_time=s, end_time=e, sub_frames=[TIT2(text=[t])])
        )
    print("audio after edit")
    print(audio)
    audio.save()


if __name__ == "__main__":
    episode_name, _ = determine_episode_name_and_number(sys.argv[1])

    tagger = AudioTagger(episode_name)
    tagger.add_tags()
    # add_tags(episode_name)
