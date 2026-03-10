from __future__ import annotations

import logging
from typing import NamedTuple

import cv2
import numpy as np
from mss import mss

from .config import Config

logger = logging.getLogger(__name__)


class Region(NamedTuple):
    """A rectangular capture area (same dict‑layout as mss expects)."""
    top: int
    left: int
    width: int
    height: int

    def as_dict(self) -> dict:
        return {"top": self.top, "left": self.left,
                "width": self.width, "height": self.height}


class ScreenGrabber:
    """Screenshot helper built on top of mss.

    Improvements over the previous version:
    - cv2 is imported at module level (no lazy per‑call import).
    - mss returns BGRA frames; conversion is now BGRA→GRAY (was BGR→GRAY,
      which silently produced wrong greyscale values).
    - Supports optional region captures so the detector only searches in the
      part of the screen that actually matters (faster + more accurate).
    """

    def __init__(self, monitor: dict | None = None) -> None:
        self.monitor = monitor or Config.MONITOR

    # ------------------------------------------------------------------
    # Raw capture
    # ------------------------------------------------------------------

    def grab(self) -> np.ndarray:
        """Capture the full monitor as a BGRA numpy array."""
        with mss() as sct:
            return np.array(sct.grab(self.monitor))

    def grab_region(self, region: Region | dict) -> np.ndarray:
        """Capture an arbitrary rectangular region."""
        area = region.as_dict() if isinstance(region, Region) else region
        with mss() as sct:
            return np.array(sct.grab(area))

    # ------------------------------------------------------------------
    # Greyscale frames (the detector works on greyscale)
    # ------------------------------------------------------------------

    def grab_gray(self) -> np.ndarray:
        """Full‑monitor greyscale screenshot.

        mss outputs *BGRA*, so we use COLOR_BGRA2GRAY (not BGR2GRAY).
        """
        return cv2.cvtColor(self.grab(), cv2.COLOR_BGRA2GRAY)

    def grab_region_gray(self, region: Region | dict) -> np.ndarray:
        """Region‑limited greyscale screenshot – faster than full capture."""
        return cv2.cvtColor(self.grab_region(region), cv2.COLOR_BGRA2GRAY)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def resolution(self) -> tuple[int, int]:
        """Return (width, height) of the configured monitor region."""
        return self.monitor["width"], self.monitor["height"]
