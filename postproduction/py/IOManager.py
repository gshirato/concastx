import os

from FileHandler import get_handler_for_extension


class IOManager:
    @staticmethod
    def read(path, template_path=None, use_template_if_absent=False):
        handler = get_handler_for_extension(os.path.splitext(path)[1])
        return handler.read(path, template_path, use_template_if_absent)

    @staticmethod
    def save(content, path):
        handler = get_handler_for_extension(os.path.splitext(path)[1])
        handler.save(content, path)

    @staticmethod
    def exists(path):
        handler = get_handler_for_extension(os.path.splitext(path)[1])
        return handler.exists(path)

    @staticmethod
    def exist_or_mkdir(paths):
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"Created {path}!")
