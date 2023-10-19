import os
import json
import pandas as pd
import requests


class FileHandler:
    def read(self, path, template_path, use_template_if_absent):
        raise NotImplementedError

    def save(self, content, path):
        raise NotImplementedError

    def exists(self, path):
        return os.path.exists(path)


class JsonHandler(FileHandler):
    def read(self, path, template_path, use_template_if_absent):
        if self.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        elif use_template_if_absent:
            return self._use_template(path, template_path)
        else:
            raise FileNotFoundError(f"{path} not found.")

    def save(self, content, path):
        with open(path, "w") as f:
            json.dump(content, f, indent=4, ensure_ascii=False)

    def _use_template(self, path, template_path):
        if not self.exists(template_path):
            raise FileNotFoundError(f"Template {template_path} not found.")
        with open(template_path, "r") as f:
            data = json.load(f)
        self.save(data, path)
        return data


class CsvHandler(FileHandler):
    def read(self, path, template_path, use_template_if_absent):
        if self.exists(path):
            return pd.read_csv(path)
        elif use_template_if_absent:
            return self._use_template(path, template_path)
        else:
            raise FileNotFoundError(f"{path} not found.")

    def save(self, content, path):
        content.to_csv(path, index=False)

    def _use_template(self, path, template_path):
        if not self.exists(template_path):
            raise FileNotFoundError(f"Template {template_path} not found.")
        data = pd.read_csv(template_path)
        self.save(data, path)
        return data


class TxtHandler(FileHandler):
    def read(self, path, template_path, use_template_if_absent):
        if self.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        elif use_template_if_absent:
            return self._use_template(path, template_path)
        else:
            raise FileNotFoundError(f"{path} not found.")

    def save(self, content, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _use_template(self, path, template_path):
        if not self.exists(template_path):
            raise FileNotFoundError(f"Template {template_path} not found.")
        with open(template_path, "r", encoding="utf-8") as f:
            data = f.read()
        self.save(data, path)
        return data


class ImageHandler(FileHandler):
    ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"]

    def read(self, path, template_path, use_template_if_absent):
        # Since reading image files directly may not be trivial,
        # you might want to define what reading an image means.
        # Perhaps, for your case, it can mean reading its binary content.
        if self.exists(path):
            with open(path, "rb") as img_file:
                return img_file.read()
        elif use_template_if_absent:
            return self._use_template(path, template_path)
        else:
            raise FileNotFoundError(f"{path} not found.")

    # def save(self, content, path):
    #     # content is expected to be bytes
    #     with open(path, "wb") as img_file:
    #         img_file.write(content)

    def _use_template(self, path, template_path):
        if not self.exists(template_path):
            raise FileNotFoundError(f"Template {template_path} not found.")
        with open(template_path, "rb") as img_file:
            data = img_file.read()
        self.save(data, path)
        return data

    def save(self, url, filepath):
        """
        Saves the image from the provided URL.

        Args:
        - url (str): The URL from where the image will be downloaded.
        - filepath (str): The path of the file where the image will be saved.

        Returns:
        - None.
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()
        print(url, response)
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=65536):
                file.write(chunk)


def get_handler_for_extension(extension):
    if extension == ".json":
        return JsonHandler()
    if extension == ".csv":
        return CsvHandler()
    if extension == ".txt":
        return TxtHandler()
    if extension in ImageHandler.ALLOWED_EXTENSIONS:
        return ImageHandler()
    raise ValueError(f"No handler for file type: {extension}")
