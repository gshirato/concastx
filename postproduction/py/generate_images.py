import openai
from dotenv import load_dotenv
import os
import sys

from operate_filename import determine_episode_type_and_number
from IOManager import IOManager

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class ImageGenerator:
    def __init__(self, topics, size="512x512"):
        self.topics = topics
        self.refuse_empty_topics()
        self.size = size

    def refuse_empty_topics(self):
        """
        Refuse to generate images if there are no topics.

        Returns:
        - None.
        """
        if not self.topics:
            raise ValueError("No topics found!")

    def create_prompt(self):
        """
        Generates a prompt for OpenAI's Image API based on a given topic.

        Returns:
        - A string prompt.
        """
        return ", ".join(self.topics)

    def create_and_save_image(self, filepath):
        """
        Creates an image based on a given topic using OpenAI's Image API.

        Returns:
        - Response from the OpenAI API.
        """
        prompt = self.create_prompt()
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size=self.size,
        )
        image_url = response["data"][0]["url"]
        IOManager.save(image_url, filepath)

        print(f"Image saved to {filepath}!")


if __name__ == "__main__":
    episode_type, episode_number = determine_episode_type_and_number(sys.argv[1])
    episode_data = IOManager.read(f"json/{episode_type}/{episode_number}.json")

    image_gen = ImageGenerator(episode_data["Topics"])
    response = image_gen.create_and_save_image(
        f"../photos/ai-generated/{episode_type}/{episode_number}.jpg"
    )

    print(episode_data, response)
