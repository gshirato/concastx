from dotenv import load_dotenv
import os
import sys
from IOManager import IOManager
from operate_filename import determine_episode_type_and_number

import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def create_topics_from_markers(markers):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {
                "role": "system",
                "content": "You are a professional podcast editor.",
            },
            {
                "role": "user",
                "content": f"I have a podcast episode memo. Please read and summarize it in a list format using main points and themes in JAPANESE. This will be captivating the potential listeners. The number of items should be 5 at most. Each item should contain a keyword, possibly with a verb if appropriate, and start with an emoji to represent it. DO NOT IN ANY CIRCUMSTANCES WRITE ANYTHING ELSE. Here's the memo:{markers}",
            },
        ],
    )
    return response.choices[0].message.content.split("\n")


def get_json_file(path, template_path="json/template.json"):
    """
    Retrieve JSON data from a file or fall back to a template if the file doesn't exist.
    """
    return (
        IOManager.read_json(path)
        if os.path.exists(path)
        else IOManager.read_json(template_path)
    )


def manage_episode_data(episode_type, episode_number, markers):
    """
    Manages episode data: retrieves, updates and checks for edited episodes.

    Parameters:
    - episode_type: Type/genre of the episode.
    - episode_number: Number of the episode.
    - markers: List of markers used to generate topics.

    Returns:
    - Updated episode data.
    """
    episode_data = get_json_file(f"json/{episode_type}/{episode_number}.json")

    if episode_data.get("Edited", False):
        print(f"Episode {episode_number} is already edited.")
        sys.exit()

    episode_data["Number"] = episode_number
    episode_data["Genre"] = episode_type
    episode_data["Topics"].extend(create_topics_from_markers(markers))
    episode_data["Edited"] = True

    return episode_data


def get_markers(path):
    """
    Extract markers from a CSV file.
    """
    return IOManager.read_csv(path, sep="\t")["Name"].tolist()


def process(episode_type, episode_number):
    markers = get_markers(f"markers/{episode_type}/{episode_number}.csv")
    episode_data = manage_episode_data(episode_type, episode_number, markers)
    print(episode_data)
    IOManager.save_to_json(episode_data, f"json/{episode_type}/{episode_number}.json")


if __name__ == "__main__":
    episode_type, episode_number = determine_episode_type_and_number(sys.argv[1])
    process(episode_type, episode_number)
