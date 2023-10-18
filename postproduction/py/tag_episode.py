import sys

from mutagen.id3 import ID3, CTOCFlags, TIT2, CTOC, CHAP
from mutagen.mp3 import MP3
import numpy as np
import pandas as pd


def add_tags(episode_name):

    def parse_timestr_milliseconds(timestr):
        time_list_str = timestr.split('.')[0].split(':')
        time_list = list(map(int, time_list_str))
        if len(time_list) == 2:
            t = (time_list[0] * 60 + time_list[1]) * 1000
        if len(time_list) == 3:
            t = (time_list[0] * 3600 + time_list[1] * 60 + time_list[2]) * 1000

        return t

    mp3 = MP3(f'../episodes/{episode_name}.mp3')
    audio = ID3(f'../episodes/{episode_name}.mp3')
    df = pd.read_csv(f'markers/{episode_name}.csv', sep='\t')

    print(audio)

    start = df['Start']
    title = df['Name']
    duration = df['Duration']
    length = mp3.info.length

    start_seconds = np.array([parse_timestr_milliseconds(t) for t in start])
    duration_seconds = np.array([parse_timestr_milliseconds(t) for t in duration])

    end_seconds = start_seconds + duration_seconds
    #end_seconds.pop(0)
    #end_seconds.append(int(length) * 1000)

    child_elements = [f'chp{i}' for i in range(1, len(title) + 1)]

    audio.add(
        CTOC(
            element_id=u"toc", flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
            child_element_ids=child_elements
        )
    )

    print('-'*40)
    print('Start   End     Title')
    for elem, s, e, t in zip(child_elements, start_seconds, end_seconds, title):
        print(s, e, t)
        audio.add(
            CHAP(
                element_id=elem, start_time=s, end_time=e,
                sub_frames=[TIT2(text=[t])]
            )
        )
    print(audio)
    audio.save()


if __name__ == "__main__":
    in_ = sys.argv[1]

    add_tags(in_)

