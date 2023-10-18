import os
import sys
import json

import cv2
import numpy as np
from typing import List, Optional
from operate_filename import determine_episode_name_and_number


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

        json_file_name = (
            f"episode{self.episode_number}.json"
            if self.episode_number
            else f"{self.episode_name}.json"
        )
        self.json_file: str = os.path.join(
            self.parent_folder, "postproduction/json", json_file_name
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

    def _add_single_starr_icon(
        self,
        image: np.ndarray,
        starr: np.ndarray,
        index: int,
        start_x: int,
        start_y: int,
        step: int,
    ) -> np.ndarray:
        """
        Add a single starr icon to the image.
        """
        # Check if the starr image is square
        if starr.shape[0] != starr.shape[1]:
            raise ValueError(
                f"starr icon has to be square ({starr.shape[0]}!={starr.shape[1]})"
            )

        # Determine the region of interest (ROI) in the main image where the starr image will be placed
        y_end = -(start_y)
        y_start = y_end - starr.shape[0]
        x_end = -(start_x + step * index)
        x_start = x_end - starr.shape[1]

        roi = image[y_start:y_end, x_start:x_end]

        # Prepare the starr image and combine it with the corresponding ROI
        cropped_mask = self.crop_circle(starr.copy(), reverse=True)
        masked_roi = cv2.bitwise_and(roi, cropped_mask)
        combined_roi = cv2.bitwise_or(masked_roi, starr)

        # Place the processed starr image back into the main image
        image[y_start:y_end, x_start:x_end] = combined_roi

        return image

    def add_starr_icons_to_episode_image(
        self, episode_image: np.ndarray, starr_images: List[np.ndarray]
    ) -> np.ndarray:
        """
        出演者のアイコンをエピソード画像に追加する
        """

        # Constants
        START_X: int = 40
        START_Y: int = 20
        STEP: int = 168

        result_image: np.ndarray = episode_image.copy()

        for i, im_starr in enumerate(starr_images[::-1]):
            result_image = self._add_single_starr_icon(
                result_image, im_starr, i, START_X, START_Y, STEP
            )

        return result_image

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

    def make_concast_post_image(self) -> None:
        """
        run by main
        """
        self.check_paths()

        self.make_post_image("Gota")


def main():
    in_ = sys.argv[1]
    episode_name, episode_number = determine_episode_name_and_number(in_)
    editor = ConcastImageEditor(os.path.abspath(".."), episode_name, episode_number)
    editor.make_concast_post_image(episode_name)


if __name__ == "__main__":
    main()
