import re
import sys
import json

import glob
import pyperclip

from operate_filename import determine_episode_name_and_number

from HTMLBuilder import HTMLBuilder
from IOManager import IOManager
from EpisodeManager import EpisodeManager
from EpisodeSearcher import EpisodeSearcher

from typing import Optional, List, Dict


def create_header_html(comments=None):
    """
    create header html
    Args:
        comments: list of comments
    Returns:
        result: header html
    """
    result = '<div class="content-head">\n'

    if comments is not None:
        result += f'<p class="comments">{comments}</p>'

    result += "</div>"
    return result


def create_references_html(references_dict):
    """
    create references html
    Args:
        references_dict: dict of references

    Returns:
        result: references html
    """

    result = '<div class="references">\n<ul class="list_test-wrap">\n'
    for text, link in references_dict.items():
        result += f'<li class="list_test"><a href="{link}">{text}</a></li>\n'
    result += "</ul>\n</div>"
    return result


def read_json(path):
    """
    read json file
    Args:
        path: path to json file
    Returns:
        data: json data
    """
    try:
        with open(path, mode="r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")


def validate_episode(data, episode_name, episode_number):
    number = data["Number"]

    if episode_number is not None:
        if episode_number != number:
            raise ValueError(f"Episode number mismatch: {episode_number} != {number}")
    else:
        if episode_name != number:
            raise ValueError(f"Episode name mismatch: {episode_name} != {number}")


def format_title(data):
    number, title, starr = data["Number"], data["Title"], ", ".join(data["Starr"])

    return (
        f"# #{number} {title} ({starr})" if number.isdecimal() else f"{title} ({starr})"
    )


def format_comments(topics):
    return "<ol>" + "".join([f"<li>{t}</li>" for t in topics]) + "</ol>"


def format_comments_sns(topics):
    # ['topic 1', 'topic 2', 'topic 3'] -> ['1. topic 1', '2. topic 2', '3. topic 3']
    return "\n".join([f"{i + 1}. {topic}" for i, topic in enumerate(topics)])


def _create_post(episode_name, episode_number=None):
    """
    create post
    Args:
        episode_name: name of episode
        episode_number: number of episode
    """
    data = read_json(f"json/{episode_name}.json")

    validate_episode(data, episode_name, episode_number)

    title = format_title(data)
    comments = format_comments(data["Topics"])
    comments_sns = format_comments_sns(data["Topics"])

    header_html = create_header_html(comments)
    references_html = create_references_html(data["References"])

    result_html = title + header_html + references_html

    pyperclip.copy(result_html)
    print("Copied to clipboard!")

    _ = write_sns_post(title, comments_sns, episode_name, episode_number)


def generate_sns_template(title: str, comments: str) -> str:
    """
    Generate the SNS template.

    Args:
        title: Title of the post.
        comments: Comments for the post.

    Returns:
        str: Formatted SNS template.
    """
    return f"""{title}

{comments}

#コンキャスト #concast
🙌視聴はこちらから https://linktr.ee/concastx"""


def save_to_txt(content: str, filename: str) -> None:
    """
    Save content to a text file.

    Args:
        content: The content to be saved.
        filename: The name of the file to which the content will be saved.

    Returns:
        None
    """
    with open(filename, mode="w", encoding="utf-8") as file:
        file.write(content)
    print(f"Wrote content to {filename}!")


def write_sns_post(
    title: str, comments: str, episode_name: str, episode_number: Optional[str] = None
) -> str:
    """
    Write an SNS post.

    Args:
        title: Title of the post.
        comments: Comments for the post.
        episode_name: Name of the episode.
        episode_number: (Optional) Number of the episode.

    Returns:
        str: Formatted SNS text.
    """
    sns_template = generate_sns_template(title, comments)

    # Constructing the file path based on episode name
    file_path = f"sns/{episode_name}.txt"

    # Saving to txt using the extracted function
    save_to_txt(sns_template, file_path)

    return sns_template


def convert_text_to_int(text):
    """
    Human sorting
    See: https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    """
    return int(text) if text.isdigit() else text


def natural_keys(data):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [convert_text_to_int(c) for c in re.split(r"(\d+)", data["number"])]


def generate_related_episodes_header() -> str:
    """
    Generate header for related episodes.

    Returns:
        str: Header string for related episodes.
    """
    return "<h3>関連エピソード</h3>"


def generate_related_episodes_list(links: List[Dict[str, str]]) -> str:
    """
    Generate list of related episodes.

    Args:
        links: List of related episode links.

    Returns:
        str: Formatted related episodes list.
    """
    links_list = "\n".join([l["link"] for l in links])
    return f"<ul>\n{links_list}\n</ul>"


def _get_related_episodes(episode_name: str, episode_number: str) -> None:
    """
    Print related episodes.

    Args:
        episode_name: Name of the episode.
        episode_number: Number of the episode.

    Returns:
        None
    """
    print(episode_name)
    data = read_json(f"json/{episode_name}.json")

    number = data["Number"]
    attrs = {"title": [number.split("-")[0]], "starrs": list(data["Starr"].keys())}

    # Remove a predefined value; this can be configured or passed as an argument
    predefined_value_to_remove = "Gota"
    if predefined_value_to_remove in attrs["starrs"]:
        attrs["starrs"].remove(predefined_value_to_remove)

    links = search_episodes(attrs)
    links = sorted(links, key=natural_keys)

    print(generate_related_episodes_header())
    print(generate_related_episodes_list(links))


def matches_title(d: dict, target_title: str) -> bool:
    """
    Check if episode matches the target title.

    Args:
        d: Episode data.
        target_title: Target title to match.

    Returns:
        bool: True if episode matches the target title, otherwise False.
    """
    valid_titles = ["hwn", "football", "weshow"]
    episode_title = d["Number"].split("-")[0]
    return episode_title in valid_titles and episode_title == target_title


def matches_starr(d: dict, starrs: list) -> bool:
    """
    Check if episode has any of the target starrs.

    Args:
        d: Episode data.
        starrs: List of target starrs.

    Returns:
        bool: True if episode has any of the target starrs, otherwise False.
    """
    return any(starr in d["Starr"] for starr in starrs)


def search_episodes(attrs: dict) -> list:
    """
    Search episodes by attributes.

    Args:
        attrs: Attributes to match.

    Returns:
        list: List of matching episodes.
    """
    results = []
    to_show = []
    count = 0
    files = glob.glob("json/*.json")

    for file_path in files:
        episode_data = read_json(file_path)
        if matches_title(episode_data, attrs["title"]) or matches_starr(
            episode_data, attrs["starrs"]
        ):
            number = episode_data["Number"]
            to_show.append(
                {
                    "file": file_path,
                    "name": episode_data["Title"],
                }
            )
            results.append(
                {
                    "link": f'<li><a href="https://sports-con.xyz/concast-{number}/">[#{number}] {episode_data["Title"]}</a></li>',
                    "number": number,
                }
            )
            count += 1

    print(f"There are {count} files found.\n")
    for entry in to_show:
        print(entry)

    return results


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
