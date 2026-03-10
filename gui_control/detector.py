from pathlib import Path
from typing import Iterable, List

import cv2
import numpy as np

from .exceptions import NoObjectFound


class TemplateDetector:
    def __init__(self, templates_dir: Path, threshold: float):
        self.templates_dir = templates_dir
        self.threshold = threshold
        self._templates = self._load_templates()

    def _load_templates(self) -> Iterable[np.ndarray]:
        if not self.templates_dir.exists():
            raise FileNotFoundError(
                f"Templates dir not found: {self.templates_dir}")

        for path in self.templates_dir.iterdir():
            if not path.is_file():
                continue
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                # log at caller if needed
                continue
            yield img

    def find(self, image: np.ndarray) -> List[np.ndarray]:
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)

        for tpl in self._templates:
            res = cv2.matchTemplate(image, tpl, cv2.TM_CCOEFF_NORMED)
            _, maxv, _, maxloc = cv2.minMaxLoc(res)
            if maxv >= self.threshold:
                top_left = maxloc
                br = (top_left[0] + tpl.shape[1], top_left[1] + tpl.shape[0])
                cv2.rectangle(mask, top_left, br, 255, 2)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise NoObjectFound("no object detected")
        return contours
