import sys
from operate_filename import determine_episode_type_and_number

import tag_episode
import create_episode_data
import post
import cv

if __name__ == "__main__":
    episode_type, episode_number = determine_episode_type_and_number(sys.argv[1])

    tag_episode.process(episode_type, episode_number)
    create_episode_data.process(episode_type, episode_number)
    post.process(episode_type, episode_number)
    cv.process(episode_type, episode_number)
