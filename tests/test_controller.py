import numpy as np
import pytest
from pathlib import Path
from unittest.mock import patch

from gui_control.controller import GuiController
from gui_control.detector import Match, TemplateDetector
from gui_control.screenshot import ScreenGrabber
from gui_control.exceptions import ClickFailure, NoObjectFound
from gui_control.config import Config


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

class FakeGrabber(ScreenGrabber):
    def __init__(self, image: np.ndarray):
        self._img = image

    def grab_gray(self):
        return self._img

    def grab_region_gray(self, region):
        return self._img


class FakeDetector(TemplateDetector):
    def __init__(self, matches: list):
        self._matches = matches

    def find(self, image):
        if not self._matches:
            raise NoObjectFound()
        return self._matches

    def find_best(self, image):
        return self.find(image)[0]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_click_uses_center_of_match(monkeypatch):
    match = Match(x=100, y=200, w=40, h=30, score=0.95)
    controller = GuiController(
        grabber=FakeGrabber(np.zeros((300, 400), dtype=np.uint8)),
        detector=FakeDetector([match]),
        jitter=0,  # disable jitter for predictable coordinates
    )

    moves = []
    monkeypatch.setattr("pyautogui.moveTo", lambda x, y, **kw: moves.append((x, y)))
    monkeypatch.setattr("pyautogui.leftClick", lambda: None)

    assert controller.click() is True
    assert moves == [(match.center_x, match.center_y)]


def test_click_failure_after_retries():
    controller = GuiController(
        grabber=FakeGrabber(np.zeros((100, 100), dtype=np.uint8)),
        detector=FakeDetector([]),  # always raises NoObjectFound
        jitter=0,
    )
    with pytest.raises(ClickFailure):
        controller.click(retries=2)


def test_click_with_template_dir(monkeypatch, tmp_path):
    import cv2
    # write a minimal template
    tpl = np.full((10, 10), 200, dtype=np.uint8)
    (tmp_path).mkdir(exist_ok=True)
    cv2.imwrite(str(tmp_path / "btn.png"), tpl)

    screen = np.zeros((80, 80), dtype=np.uint8)
    screen[10:20, 10:20] = tpl

    controller = GuiController(
        grabber=FakeGrabber(screen),
        detector=FakeDetector([]),  # default detector is irrelevant here
        jitter=0,
    )

    moved = []
    monkeypatch.setattr("pyautogui.moveTo", lambda x, y, **kw: moved.append((x, y)))
    monkeypatch.setattr("pyautogui.leftClick", lambda: None)

    result = controller.click(template_dir=tmp_path, retries=1)
    assert result is True
    assert moved, "moveTo should have been called"


def test_click_template_no_duplicates(monkeypatch):
    called_paths = []

    controller = GuiController(
        grabber=FakeGrabber(np.zeros((100, 100), dtype=np.uint8)),
        detector=FakeDetector([]),
        jitter=0,
    )

    def fake_click(path, retries=None, region=None):
        called_paths.append(path)
        return False

    monkeypatch.setattr(controller, "click", fake_click)

    # Using the same dir twice should not create duplicate candidates
    controller.click_template("foo", template_dirs=["/a", "/a"])
    # /a/foo should appear only once
    assert called_paths.count(Path("/a/foo")) <= 1


def test_jitter_applied(monkeypatch):
    match = Match(x=50, y=50, w=10, h=10, score=0.9)
    controller = GuiController(
        grabber=FakeGrabber(np.zeros((200, 200), dtype=np.uint8)),
        detector=FakeDetector([match]),
        jitter=20,
    )
    moves = []
    monkeypatch.setattr("pyautogui.moveTo", lambda x, y, **kw: moves.append((x, y)))
    monkeypatch.setattr("pyautogui.leftClick", lambda: None)

    controller.click()
    assert moves
    cx, cy = moves[0]
    # with jitter=20, position should differ from perfect center up to ±20
    assert abs(cx - match.center_x) <= 20
    assert abs(cy - match.center_y) <= 20
