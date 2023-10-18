from re import search
import sys
import json

from attr import attr
import glob
import pyperclip

from operate_filename import determine_episode_name_and_number


def create_header_html(comments=None):
    """
    create header html
    Args:
        comments: list of comments
    Returns:
        result: header html
    """
    result = '<div class="content-head">\n'

    if comments is not None:
        result += f'<p class="comments">{comments}</p>'

    result += "</div>"
    return result


def create_references_html(references_dict):
    """
    create references html
    Args:
        references_dict: dict of references

    Returns:
        result: references html
    """

    result = '<div class="references">\n'
    result += '<ul class="list_test-wrap">\n'
    for text, link in references_dict.items():
        result += f'<li class="list_test"><a href="{link}">{text}</a></li>\n'
    result += "</ul>\n\n"
    result += "</div>"
    return result


def read_json(path):
    """
    read json file
    Args:
        path: path to json file
    Returns:
        data: json data
    """
    try:
        with open(path, mode="r") as f:
            return json.load(f)
    except:
        raise ValueError("File not found:", path)


def create_post(episode_name, episode_number=None):
    """
    create post
    Args:
        episode_name: name of episode
        episode_number: number of episode
    """
    data = read_json(f"json/{episode_name}.json")

    number = data["Number"]
    title = data["Title"]
    topics = data["Topics"]
    starr = ", ".join(data["Starr"])

    if episode_name.split("episode")[-1] != number:
        raise ValueError("Episode number is wrong.")

    if number.isdecimal():
        title = f"#{number} {title} ({starr})"
    else:
        title = f"{title} ({starr})"

    topics = list(map(lambda x: x, topics))
    comments = "<ol>" + "".join([f"<li>{t}</li>" for t in topics]) + "</ol>"

    # ['topic 1', 'topic 2', 'topic 3'] -> ['1. topic 1', '2. topic 2', '3. topic 3']
    topics_sns = list(map(lambda i_x: f"{i_x[0] + 1}. {i_x[1]}", enumerate(topics)))
    comments_sns = "\n".join(topics_sns)

    references = data["References"]
    header_html = create_header_html(comments)
    references_html = create_references_html(references)

    result_html = title + header_html + references_html

    pyperclip.copy(result_html)
    print("Copied to clipboard!")

    _ = write_sns_post(title, comments_sns, episode_name, episode_number)


def write_sns_post(title, comments, episode_name, episode_number=None):
    """
    write sns post
    Args:
        title: title of post
        comments: comments of post
        episode_name: name of episode
        episode_number: number of episode

    Returns:
        sns_text: sns text
    """
    if episode_number is not None:
        url = f"https://sports-con.xyz/concast-{episode_number}/"
    else:
        url = f"https://sports-con.xyz/concast-{episode_name}/"

    texts = [
        title,
        comments,
        "#コンキャスト #concast",
        "👇視聴はこちらから https://linktr.ee/concastx",
    ]
    sns_text = "\n\n".join(texts)

    with open(f"sns/{episode_name}.txt", mode="w") as f:
        f.write(sns_text)

    print("Wrote SNS post!")

    return sns_text


def make_feed(in_):
    """
    could be used as main()
    """
    in_ = sys.argv[1]

    episode_name, episode_number = determine_episode_name_and_number(in_)
    create_post(episode_name, episode_number)


# Human Sorting
# https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(data):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    text = data["number"]
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def get_relative_episodes(in_):
    """
    can be used as main()
    """
    if in_.isdecimal():
        episode_name = f"episode{in_}"
    else:
        if len(in_.split("-")) == 2:
            # e.g. football-15
            try:
                episode_number, aftertalk_number = map(int, in_.split("-"))
                episode_name = f"episode{episode_number}-{aftertalk_number}"
            except BaseException:
                episode_name = in_
        elif len(in_.split("-")) == 3:
            # e.g. football-16-1
            episode_name = in_
        else:
            raise BaseException(f"invalid input: {in_}")
    print(episode_name)
    data = read_json(f"json/{episode_name}.json")

    number = data["Number"]
    starr = ", ".join(data["Starr"])

    attrs = {"title": [], "starrs": list(data["Starr"].keys())}
    attrs["title"].append(number.split("-")[0])
    attrs["starrs"].remove("Gota")

    links = search_episodes(attrs)
    links = sorted(links, key=natural_keys)

    print("<h3>関連エピソード</h3>")
    print("<ul>")
    for l in links:
        print(l["link"])
    else:
        print("</ul>")


def search_episodes(attrs):
    res = []
    to_show = []
    count = 0
    files = glob.glob("json/*.json")
    for f in files:
        is_valid = False
        d = read_json(f)
        if (
            d["Number"].split("-")[0] in ["hwn", "football", "weshow"]
            and d["Number"].split("-")[0] == attrs["title"]
        ):
            is_valid = True
            count += 1
        for starr in attrs["starrs"]:
            if starr in d["Starr"]:
                is_valid = True
        if is_valid:
            number = d["Number"]
            to_show.append(
                {
                    "file": f,
                    "name": d["Title"],
                }
            )
            res.append(
                {
                    "link": f'<li><a href="https://sports-con.xyz/concast-{number}/">[#{number}] {d["Title"]}</a></li>',
                    "number": number,
                }
            )
            count += 1

    else:
        print(f"There are {count} files found.\n")

    for e in to_show:
        print(e)
    return res


if __name__ == "__main__":
    in_ = sys.argv[1]
    make_feed(in_)
    get_relative_episodes(in_)
