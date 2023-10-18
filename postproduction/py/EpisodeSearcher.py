import re
import glob

from IOManager import IOManager


class EpisodeSearcher:
    @staticmethod
    def convert_text_to_int(text):
        return int(text) if text.isdigit() else text

    @staticmethod
    def natural_keys(data):
        return [
            EpisodeSearcher.convert_text_to_int(c)
            for c in re.split(r"(\d+)", data["number"])
        ]

    @staticmethod
    def matches_title(d: dict, target_title: str) -> bool:
        valid_types = ["hwn", "football", "weshow"]
        episode_type = d["Number"].split("-")[0]
        return episode_type in valid_types and episode_type == target_title

    @staticmethod
    def matches_starr(d: dict, starrs: list) -> bool:
        return any(starr in d["Starr"] for starr in starrs)

    @staticmethod
    def search_episodes(attrs: dict) -> list:
        results = []
        to_show = []
        count = 0
        files = glob.glob(f"json/{attrs['episode-type']}/*.json")
        predefined_value_to_remove = "Gota"
        print()
        for file_path in files:
            episode_data = IOManager.read_json(file_path)
            # remove 'Gota' from episode_data['Starr']
            if predefined_value_to_remove in attrs["starrs"]:
                attrs["starrs"].remove(predefined_value_to_remove)
            if EpisodeSearcher.matches_title(
                episode_data, attrs["episode-type"]
            ) or EpisodeSearcher.matches_starr(episode_data, attrs["starrs"]):
                number = episode_data["Number"]
                to_show.append({"file": file_path, "name": episode_data["Title"]})
                results.append(
                    {
                        "link": f'<li><a href="https://sports-con.xyz/concast-{number}/">[#{number}] {episode_data["Title"]}</a></li>',
                        "number": number,
                    }
                )
                count += 1

        for entry in to_show:
            print(f"{entry['file']: <30}{entry['name']}")

        return results
