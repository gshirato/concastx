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


def get_json_file(path):
    if os.path.exists(path):
        return IOManager.read_json(path)
    return IOManager.read_json("json/template.json")


def get_markers(path):
    return IOManager.read_csv(path, sep="\t")["Name"].tolist()


if __name__ == "__main__":
    episode_type, episode_number = determine_episode_type_and_number(sys.argv[1])
    markers = get_markers(f"markers/{episode_type}/{episode_number}.csv")
    episode_data = get_json_file(f"json/{episode_type}/{episode_number}.json")
    if episode_data.get("Edited", False):
        print(f"Episode {episode_number} is already edited.")
        sys.exit()
    episode_data["Number"] = episode_number
    episode_data["Genre"] = episode_type
    topics = create_topics_from_markers(markers)
    episode_data["Topics"].extend(topics)
    episode_data["Edited"] = True

    print(episode_data)

    IOManager.save_to_json(episode_data, f"json/{episode_type}/{episode_number}.json")
