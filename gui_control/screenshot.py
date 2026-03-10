from pathlib import Path
from typing import Tuple

import numpy as np
from mss import mss

from .config import Config


class ScreenGrabber:
    """Wrapper around mss for grabbing the monitor area defined in config."""

    def __init__(self, monitor=None):
        self.monitor = monitor or Config.MONITOR

    def grab(self) -> np.ndarray:
        with mss() as sct:
            screenshot = sct.grab(self.monitor)
            return np.array(screenshot)

    def grab_gray(self) -> np.ndarray:
        img = self.grab()
        # convert BGR->GRAY
        import cv2

        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
