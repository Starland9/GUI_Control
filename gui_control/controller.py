from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import Iterable

import pyautogui

from .config import Config
from .detector import Match, TemplateDetector
from .exceptions import ClickFailure
from .screenshot import Region, ScreenGrabber

logger = logging.getLogger(__name__)

# Make pyautogui safer: raises an exception on fail instead of hanging.
pyautogui.FAILSAFE = True


class GuiController:
    """Performs mouse / keyboard actions based on on‑screen detections.

    Design goals:
    - ``click()`` accepts an optional *template_dir* so actions can target any
      template folder without constructing a new controller.
    - Click coordinates use the *centre* of the matched bounding box (much
      more reliable than an arbitrary contour point).
    - A small random jitter is applied so repeated clicks feel human‑like and
      are less likely to be blocked by anti‑automation measures.
    - ``click_template()`` resolves a name across multiple directories without
      adding duplicate candidate paths.
    """

    def __init__(
        self,
        grabber: ScreenGrabber,
        detector: TemplateDetector,
        *,
        jitter: int = 5,
    ) -> None:
        """
        Parameters
        ----------
        grabber:
            Provides screen frames.
        detector:
            Default detector (used when no *template_dir* is supplied to
            :meth:`click`).
        jitter:
            Maximum pixel offset applied randomly to the click position to
            make movements look more human.  Set to 0 to disable.
        """
        self.grabber = grabber
        self.detector = detector
        self.jitter = jitter

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _jitter(self, x: int, y: int) -> tuple[int, int]:
        if self.jitter == 0:
            return x, y
        return (
            x + random.randint(-self.jitter, self.jitter),
            y + random.randint(-self.jitter, self.jitter),
        )

    def _click_match(self, match: Match) -> None:
        cx, cy = self._jitter(match.center_x, match.center_y)
        logger.debug("Clicking (%d, %d) — score %.3f", cx, cy, match.score)
        pyautogui.moveTo(cx, cy, duration=Config.MOUSE_MOVE_DURATION)
        pyautogui.leftClick()

    # ------------------------------------------------------------------
    # Core click API
    # ------------------------------------------------------------------

    def click(
        self,
        template_dir: Path | None = None,
        retries: int | None = None,
        region: Region | dict | None = None,
    ) -> bool:
        """Detect the first template match and click its centre.

        Parameters
        ----------
        template_dir:
            If supplied, a throw‑away :class:`TemplateDetector` is built for
            that directory; otherwise the controller's default detector is used.
        retries:
            Number of attempts before giving up.  Defaults to
            :attr:`Config.MAX_RETRIES`.
        region:
            Optional screen region to limit the capture (faster, less noise).
        """
        retries = retries if retries is not None else Config.MAX_RETRIES
        for attempt in range(max(1, retries)):
            try:
                if region is not None:
                    img = self.grabber.grab_region_gray(region)
                else:
                    img = self.grabber.grab_gray()

                if template_dir is not None:
                    temp_detector = TemplateDetector(
                        template_dir, Config.TEMPLATE_MATCH_THRESHOLD
                    )
                    match = temp_detector.find_best(img)
                else:
                    match = self.detector.find_best(img)

                self._click_match(match)
                return True

            except Exception as exc:
                if attempt == retries - 1:
                    raise ClickFailure(exc) from exc
                logger.warning(
                    "click attempt %d/%d failed: %s", attempt + 1, retries, exc
                )
                time.sleep(Config.RETRY_DELAY)

        return False  # unreachable but satisfies type checkers

    def click_template(
        self,
        name: str,
        template_dirs: Iterable[str] | None = None,
        retries: int | None = None,
        region: Region | dict | None = None,
    ) -> bool:
        """Resolve *name* across one or more directories and click it.

        Candidate directories are tried in order; the global
        :attr:`Config.TEMPLATES_DIR` is always tried last.  Duplicate paths are
        skipped automatically.
        """
        seen: set[Path] = set()
        candidates: list[Path] = []

        def _add(p: Path) -> None:
            if p not in seen:
                seen.add(p)
                candidates.append(p)

        if template_dirs:
            for d in template_dirs:
                base = Path(d)
                # prefer  d/name  if d is a directory, otherwise  d  directly
                _add(base / name if base.is_dir() else base)

        # global fallback
        _add(Path(Config.TEMPLATES_DIR) / name)

        for path in candidates:
            try:
                if self.click(path, retries=retries, region=region):
                    return True
            except ClickFailure:
                logger.debug("Candidate %s did not match", path)
                continue

        return False

    # ------------------------------------------------------------------
    # Keyboard / utility helpers
    # ------------------------------------------------------------------

    def press_key(self, key: str, times: int = 1) -> None:
        """Press a single key one or more times."""
        for _ in range(times):
            pyautogui.press(key)

    def press_tab(self, times: int = 1) -> None:
        for _ in range(times):
            pyautogui.press("tab")

    def hotkey(self, *keys: str) -> None:
        """Fire a keyboard shortcut (e.g. ``ctrl``, ``c``)."""
        pyautogui.hotkey(*keys)

    def type_text(self, text: str, interval: float | None = None) -> None:
        """Type a string character by character."""
        pyautogui.typewrite(text, interval=interval or Config.TYPE_DELAY)

    def move_to(self, x: int, y: int) -> None:
        pyautogui.moveTo(x, y, duration=Config.MOUSE_MOVE_DURATION)

    def click_at(self, x: int, y: int) -> None:
        """Click at an absolute screen coordinate."""
        cx, cy = self._jitter(x, y)
        pyautogui.moveTo(cx, cy, duration=Config.MOUSE_MOVE_DURATION)
        pyautogui.leftClick()
