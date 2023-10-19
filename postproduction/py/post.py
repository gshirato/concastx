import sys
import pyperclip

from operate_filename import determine_episode_type_and_number

from HTMLBuilder import HTMLBuilder
from IOManager import IOManager
from EpisodeManager import EpisodeManager
from EpisodeSearcher import EpisodeSearcher


def create_post(episode_type, episode_number):
    data = IOManager.read(f"json/{episode_type}/{episode_number}.json")

    EpisodeManager.validate_episode(data, episode_type, episode_number)
    title = EpisodeManager.format_title(data)
    references_html = HTMLBuilder.create_references_html(data["References"])
    if "Topics" in data:
        topics_html = HTMLBuilder.create_header_html(
            EpisodeManager.format_comments(data["Topics"])
        )
        pyperclip.copy(f"# {title}{topics_html}{references_html}")

        sns_post = EpisodeManager.create_sns_post(data)

        IOManager.save(sns_post, f"sns/{episode_type}/{episode_number}.txt")


def get_related_episodes(episode_type, episode_number):
    data = IOManager.read(f"json/{episode_type}/{episode_number}.json")
    attrs = {
        "episode-type": episode_type,
        "starrs": list(data["Starr"].keys()),
    }
    related_episodes = EpisodeSearcher.search_episodes(attrs)
    related_episodes.sort(key=EpisodeSearcher.natural_keys)

    if related_episodes:
        print(HTMLBuilder.generate_related_episodes_header())
        print(HTMLBuilder.generate_related_episodes_list(related_episodes))


def process(episode_type, episode_number):
    create_post(episode_type, episode_number)
    get_related_episodes(episode_type, episode_number)


if __name__ == "__main__":
    episode_type, episode_number = determine_episode_type_and_number(sys.argv[1])
    process(episode_type, episode_number)
