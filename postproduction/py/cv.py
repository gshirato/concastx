import os
import sys
import json

import cv2
import numpy as np


def get_starrs(path):
    """
    出演者の名前を取得する
    """
    with open(path) as f:
        return json.load(f)["Starr"].keys()


def path_exists(path):
    return os.path.exists(path)


def get_icon(path, resolution=128**2):
    print(path)
    icon = cv2.imread(path)
    h, w, c = icon.shape
    scale = (resolution / (h * w)) ** 0.5
    return cv2.resize(icon, None, fx=scale, fy=scale)


def reverse_image(im, mask, reverse):
    if reverse:
        mask = im | mask
        im |= mask
        return 255 - im
    return im & mask


def crop_circle(im, reverse=False):
    """正方形に画像をクロップ"""
    h, _, _ = im.shape[0]

    center = int(h / 2)
    mask = np.zeros(im.shape, np.uint8)
    cv2.circle(
        mask, (center, center), radius=center, color=(255, 255, 255), thickness=-1
    )

    return reverse_image(im, mask, reverse)


def get_starr_images(host, **kwargs):
    parent_folder = kwargs["parent_folder"]
    json_folder = kwargs["json_folder"]

    starrs = get_starrs(json_folder)

    starr_images = []

    for starr in starrs:
        if starr == host:
            starr += f"-{np.random.randint(1, 3)}"

        icon_path = os.path.join(parent_folder, f"photos/starrings/{starr}.jpg")
        assert path_exists(json_folder), f"path not found: {json_folder}"

        icon = get_icon(icon_path)
        icon = crop_circle(icon)
        starr_images.append(icon)
    return starr_images


def crop_episode_image_to_square(episode_image, podcast_icon_path, alpha=0.3):
    _episode_image = episode_image.copy()

    color_filter_overlay = episode_image.copy()

    x, y, w, h = cv2.selectROI("resize", _episode_image)
    size = min(w, h)

    cv2.rectangle(
        color_filter_overlay,
        (x, y),
        (x + size, y + size),
        (255, 255, 255, 0.3),
        cv2.FILLED,
    )

    _episode_image = cv2.addWeighted(
        color_filter_overlay, alpha, _episode_image, 1 - alpha, 0
    )
    _episode_image = _episode_image[y : y + size, x : x + size]

    concast_icon = get_icon(podcast_icon_path)

    _episode_image[
        -(20 + concast_icon.shape[0]) : -20, 30 : 30 + concast_icon.shape[1]
    ] = concast_icon

    return _episode_image


def add_starr_icons_to_episode_image(episode_image, starr_images):
    """出演者のアイコンをエピソード画像に追加する"""
    _episode_image = episode_image.copy()

    i = 0
    for im_starr in starr_images[::-1]:
        assert (
            im_starr.shape[0] == im_starr.shape[1]
        ), f"starr icon has to be square ({im_starr.shape[0]}!={im_starr.shape[1]})"
        start_x = 40
        start_y = 20
        step = 168
        roi = _episode_image[
            -(start_y + im_starr.shape[0]) : -(start_y),
            -(start_x + step * i + im_starr.shape[1]) : -(start_x + step * i),
        ]
        cropped_mask = crop(im_starr.copy(), reverse=True)
        masked_roi = cv2.bitwise_and(roi, cropped_mask)
        final_roi = cv2.bitwise_or(masked_roi, im_starr)
        _episode_image[
            -(start_y + im_starr.shape[0]) : -(start_y),
            -(start_x + step * i + im_starr.shape[1]) : -(start_x + step * i),
        ] = final_roi

        i += 1
    return _episode_image


def make_concast_post_image(episode_name, episode_number=None):
    """
    run by main
    """

    parent_folder = os.path.abspath("..")

    episode_image_path = os.path.join(
        parent_folder, f"photos/eyecatch/{episode_name}.jpg"
    )
    podcast_icon_path = os.path.join(parent_folder, "concast.png")

    output_filename = (
        f"icon-{episode_number}.jpg" if episode_number else f"icon-{episode_name}.jpg"
    )

    output_file = os.path.join(parent_folder, f"photos/editted-icon/{output_filename}")

    kwargs = {
        "episode_image_path": episode_image_path,
        "podcast_icon_path": podcast_icon_path,
        "output_file": output_file,
    }

    check_paths(**kwargs)

    make_post_image("Gota", **kwargs)


def check_paths(**kwargs):
    for name in ["parent_folder", "json_folder", "episode_image_path"]:
        path = kwargs[name]
        assert path_exists(path), f"path for `{name}`` not found: {path}"


def make_post_image(host, **kwargs):
    episode_image_path = kwargs["episode_image_path"]
    podcast_icon_path = kwargs["podcast_icon_path"]
    output_file = kwargs["output_file"]

    starr_images = get_starr_images(host, **kwargs)

    episode_image = cv2.imread(episode_image_path)

    episode_image = crop_episode_image_to_square(episode_image, podcast_icon_path)

    episode_image = add_starr_icons_to_episode_image(episode_image, starr_images)

    cv2.imshow("Result", episode_image)
    k = cv2.waitKey(0)

    if k == ord("q"):
        raise Exception("process cancelled.")

    else:
        cv2.imwrite(output_file, episode_image)
        print(f"saved {output_file}")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    in_ = sys.argv[1]
    if in_.isdecimal():
        episode_name = f"episode{in_}"
        make_concast_post_image(episode_name, in_)
    else:
        if len(in_.split("-")) == 2:
            try:
                episode_number, aftertalk_number = map(int, in_.split("-"))
                episode_name = f"episode{episode_number}-{aftertalk_number}"
            except Exception as e:
                print(f"An error occurred: {e}")
                episode_name = in_
        elif len(in_.split("-")) == 3:
            # e.g. football-16-1
            episode_name = in_
        else:
            raise BaseException(f"invalid input: {in_}")
        make_concast_post_image(episode_name)