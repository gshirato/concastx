import json
import os
import pandas as pd


class IOManager:
    @staticmethod
    def read_csv(path, sep=","):
        try:
            return pd.read_csv(path, sep=sep)
        except FileNotFoundError:
            raise ValueError(f"File not found: {path}")

    @staticmethod
    def read_json(path):
        try:
            with open(path, mode="r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"File not found: {path}")

    @staticmethod
    def save_to_json(content, path):
        with open(path, mode="w") as f:
            json.dump(content, f, indent=4, ensure_ascii=False)
        print(f"Wrote json to {path}!")

    @staticmethod
    def save_to_txt(content: str, filename: str):
        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(content)
        print(f"Wrote txt to {filename}!")

    @staticmethod
    def save_df_to_csv(df, filename, index=False):
        df.to_csv(filename, index=index)
        print(f"Wrote df to {filename}!")

    @staticmethod
    def exist_or_mkdir(paths):
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"Created {path}!")
