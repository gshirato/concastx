import os
import sys
import json

import cv2
import numpy as np
from typing import List, Tuple, Union, Optional


class ConcastImageEditor:
    def __init__(
        self,
        parent_folder: str,
        episode_name: str,
        episode_number: Optional[str] = None,
    ):
        self.parent_folder: str = parent_folder
        self.episode_name: str = episode_name
        self.episode_number: Optional[str] = episode_number
        self.podcast_icon_path: str = os.path.join(self.parent_folder, "concast.png")

        self.episode_image_path: str = os.path.join(
            self.parent_folder, f"photos/eyecatch/{episode_name}.jpg"
        )
        self.podcast_icon_path: str = os.path.join(self.parent_folder, "concast.png")

        self.json_file: str = os.path.join(
            self.parent_folder, "postproduction/json", f"episode{episode_number}.json"
        )

        # Set output file path
        output_filename = (
            f"icon-{self.episode_number}.jpg"
            if self.episode_number
            else f"icon-{self.episode_name}.jpg"
        )
        self.output_file: str = os.path.join(
            self.parent_folder, f"photos/editted-icon/{output_filename}"
        )

    @staticmethod
    def path_exists(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def get_starrs(path: str) -> List[str]:
        """
        出演者の名前を取得する
        """
        with open(path) as f:
            return json.load(f)["Starr"].keys()

    @staticmethod
    def get_icon(path: str, resolution: int = 128**2) -> np.ndarray:
        print(path)
        icon: np.ndarray = cv2.imread(path)
        h, w, _ = icon.shape
        scale: float = (resolution / (h * w)) ** 0.5
        return cv2.resize(icon, None, fx=scale, fy=scale)

    @staticmethod
    def reverse_image(im: np.ndarray, mask: np.ndarray, reverse: bool) -> np.ndarray:
        if reverse:
            mask = im | mask
            im |= mask
            return 255 - im
        return im & mask

    def check_paths(self) -> None:
        for name in ["parent_folder", "json_file", "episode_image_path"]:
            path = getattr(self, name)
            assert self.path_exists(path), f"path for `{name}`` not found: {path}"

    def crop_circle(self, im: np.ndarray, reverse: bool = False) -> np.ndarray:
        """正方形に画像をクロップ"""
        h = im.shape[0]

        center: int = int(h / 2)
        mask: np.ndarray = np.zeros(im.shape, np.uint8)
        cv2.circle(
            mask, (center, center), radius=center, color=(255, 255, 255), thickness=-1
        )

        return self.reverse_image(im, mask, reverse)

    def get_starr_images(self, host: str) -> List[np.ndarray]:
        parent_folder: str = self.parent_folder
        json_file: str = self.json_file

        starrs: List[str] = self.get_starrs(json_file)

        starr_images: List[np.ndarray] = []

        for starr in starrs:
            if starr == host:
                starr += f"-{np.random.randint(1, 3)}"

            icon_path: str = os.path.join(
                parent_folder, f"photos/starrings/{starr}.jpg"
            )
            assert self.path_exists(json_file), f"path not found: {json_file}"

            icon: np.ndarray = self.get_icon(icon_path)
            icon: np.ndarray = self.crop_circle(icon)
            starr_images.append(icon)
        return starr_images

    def crop_episode_image_to_square(
        self, episode_image: np.ndarray, podcast_icon_path: str, alpha: float = 0.3
    ) -> np.ndarray:
        _episode_image: np.ndarray = episode_image.copy()

        color_filter_overlay: np.ndarray = episode_image.copy()

        x, y, w, h = cv2.selectROI("resize", _episode_image)
        size: int = min(w, h)

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

        concast_icon: np.ndarray = self.get_icon(podcast_icon_path)

        _episode_image[
            -(20 + concast_icon.shape[0]) : -20, 30 : 30 + concast_icon.shape[1]
        ] = concast_icon

        return _episode_image

    def add_starr_icons_to_episode_image(
        self, episode_image: np.ndarray, starr_images: List[np.ndarray]
    ) -> np.ndarray:
        """出演者のアイコンをエピソード画像に追加する"""
        _episode_image: np.ndarray = episode_image.copy()

        i: int = 0
        for im_starr in starr_images[::-1]:
            assert (
                im_starr.shape[0] == im_starr.shape[1]
            ), f"starr icon has to be square ({im_starr.shape[0]}!={im_starr.shape[1]})"
            start_x: int = 40
            start_y: int = 20
            step: int = 168
            roi: np.ndarray = _episode_image[
                -(start_y + im_starr.shape[0]) : -(start_y),
                -(start_x + step * i + im_starr.shape[1]) : -(start_x + step * i),
            ]
            cropped_mask: np.ndarray = self.crop_circle(im_starr.copy(), reverse=True)
            masked_roi: np.ndarray = cv2.bitwise_and(roi, cropped_mask)
            final_roi: np.ndarray = cv2.bitwise_or(masked_roi, im_starr)
            _episode_image[
                -(start_y + im_starr.shape[0]) : -(start_y),
                -(start_x + step * i + im_starr.shape[1]) : -(start_x + step * i),
            ] = final_roi

            i += 1
        return _episode_image

    def make_post_image(self, host: str) -> None:
        episode_image: np.ndarray = cv2.imread(self.episode_image_path)

        episode_image: np.ndarray = self.crop_episode_image_to_square(
            episode_image, self.podcast_icon_path
        )

        starr_images: List[np.ndarray] = self.get_starr_images(host)

        episode_image: np.ndarray = self.add_starr_icons_to_episode_image(
            episode_image, starr_images
        )

        cv2.imshow("Result", episode_image)
        k: int = cv2.waitKey(0)

        if k == ord("q"):
            raise Exception("process cancelled.")

        else:
            cv2.imwrite(self.output_file, episode_image)
            print(f"saved {self.output_file}")

        cv2.destroyAllWindows()

    def make_concast_post_image(self, episode_name: str) -> None:
        """
        run by main
        """
        self.check_paths()

        self.make_post_image("Gota")


def main():
    in_ = sys.argv[1]

    if in_.isdecimal():
        editor = ConcastImageEditor(os.path.abspath(".."), f"episode{in_}", in_)
        episode_name = f"episode{in_}"
        editor.make_concast_post_image(episode_name)
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
        editor = ConcastImageEditor(os.path.abspath(".."), episode_name)
        editor.make_concast_post_image(episode_name)


if __name__ == "__main__":
    main()
