from typing import Union
import re
import glob
import os


def determine_episode_type_and_number(input_str: Union[str, int]) -> str:
    """
    Parses an input string and returns a tuple with two strings:
    - The first string is a normalized version of the input that can be used as a key in a dictionary.
    - The second string is an optional identifier that can be used to distinguish between different versions of the same input.

    The input string can have one of the following formats:
    - A decimal number, in which case the first string is "episode" followed by the number, and the second string is the number itself.
    - Two numbers separated by a hyphen, in which case the first string is "episode" followed by the first number and the second string is the two numbers separated by a hyphen.
    - Three tokens separated by hyphens, in which case the input is returned as is.
    - Any other input is considered invalid and raises a BaseException.

    Args:
        input_str: A string representing the input to be parsed.

    Returns:
        A tuple with two strings: the normalized input and an optional identifier.
    """

    if input_str.isdecimal():
        return "concast", input_str

    tokens = input_str.split("-")

    if len(tokens) == 2:
        if tokens[0].isdecimal() and tokens[1].isdecimal():
            episode_number, aftertalk_number = map(int, tokens)
            return ("concast", "-".join(tokens))
        elif tokens[1].isdecimal():
            return tokens[0], tokens[1]
        else:
            # test-episode
            return input_str, None

    elif len(tokens) == 3:
        # e.g., football-16-1
        return tokens[0], "-".join(tokens[1:])

    raise BaseException(f"invalid input: {input_str}")


def omit_episode_type_from_filename(filename: str, type) -> str:
    """
    rename a file with a new name
    """
    if type == "concast":
        return re.sub(r"episode", "", filename)

    return re.sub(f"{type}-", "", filename)


def normalize_extension(ext: str) -> str:
    """
    normalize an extension
    """
    dict = {
        "jpeg": "jpg",
    }
    return dict.get(ext.lower(), ext.lower())


def rename_files(folder_name: str, ext: str, episode_type: str):
    """
    rename files in a directory
    """

    files = glob.glob(f"{folder_name}/{episode_type}/*.{ext}")

    for file in files:
        filename = file.split("/")[-1]
        new_filename = omit_episode_type_from_filename(filename, episode_type)
        new_ext = normalize_extension(ext)

        new_filename = new_filename.replace(ext, new_ext)

        if filename == new_filename:
            continue
        print(f"{filename} -> {new_filename}")
        os.rename(file, f"{folder_name}/{episode_type}/{new_filename}")


def main():
    """
    main function
    """

    rename_files("sns", "txt", "concast")
    rename_files("sns", "txt", "football")
    rename_files("sns", "txt", "hwn")
    rename_files("sns", "txt", "weshow")
    rename_files("sns", "txt", "solo")


if __name__ == "__main__":
    main()
