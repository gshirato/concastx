from typing import Union


def determine_episode_name_and_number(input_str: Union[str, int]) -> str:
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
        return f"episode{input_str}", input_str

    tokens = input_str.split("-")

    if len(tokens) == 2:
        try:
            episode_number, aftertalk_number = map(int, tokens)
            return (
                f"episode{episode_number}-{aftertalk_number}",
                f"{episode_number}-{aftertalk_number}",
            )
        except ValueError:
            # football-2
            return input_str, None

    elif len(tokens) == 3:
        # e.g., football-16-1
        return input_str, None

    raise BaseException(f"invalid input: {input_str}")
