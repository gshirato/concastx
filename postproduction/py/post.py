import sys
import pyperclip

from operate_filename import determine_episode_name_and_number

from HTMLBuilder import HTMLBuilder
from IOManager import IOManager
from EpisodeManager import EpisodeManager
from EpisodeSearcher import EpisodeSearcher


def create_post(episode_name, episode_number):
    data = IOManager.read_json(f"json/{episode_name}.json")

    EpisodeManager.validate_episode(data, episode_name, episode_number)
    title = EpisodeManager.format_title(data)

    if "Topics" in data:
        topics_html = HTMLBuilder.create_header_html(
            EpisodeManager.format_comments(data["Topics"])
        )
        pyperclip.copy(f"# {title}\n{topics_html}")

        sns_post = EpisodeManager.create_sns_post(data)

        IOManager.save_to_txt(sns_post, f"sns/{episode_name}.txt")


def get_related_episodes(episode_name, episode_number):
    data = IOManager.read_json(f"json/{episode_name}.json")
    attrs = {
        "episode-type": [episode_name.split("-")[0]],
        "starrs": list(data["Starr"].keys()),
    }
    related_episodes = EpisodeSearcher.search_episodes(attrs)
    related_episodes.sort(key=EpisodeSearcher.natural_keys)

    if related_episodes:
        print(HTMLBuilder.generate_related_episodes_header())
        print(HTMLBuilder.generate_related_episodes_list(related_episodes))


if __name__ == "__main__":
    in_ = sys.argv[1]
    episode_name, episode_number = determine_episode_name_and_number(in_)

    create_post(episode_name, episode_number)
    get_related_episodes(episode_name, episode_number)
