import json


class IOManager:
    @staticmethod
    def read_json(path):
        try:
            with open(path, mode="r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"File not found: {path}")

    @staticmethod
    def save_to_txt(content: str, filename: str):
        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(content)
        print(f"Wrote content to {filename}!")
