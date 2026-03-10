import numpy as np
import pytest

from gui_control.controller import GuiController
from gui_control.screenshot import ScreenGrabber
from gui_control.detector import TemplateDetector
from gui_control.config import Config
from gui_control.exceptions import ClickFailure, NoObjectFound


class DummyGrabber(ScreenGrabber):
    def __init__(self, image):
        self._img = image

    def grab_gray(self):
        return self._img


class DummyDetector(TemplateDetector):
    def __init__(self, contours):
        self._contours = contours

    def find(self, image):
        if not self._contours:
            raise NoObjectFound()
        return self._contours


def test_click_success(monkeypatch):
    img = np.zeros((10, 10), dtype=np.uint8)
    grabber = DummyGrabber(img)
    contours = [np.array([[[1, 2]]])]
    detector = DummyDetector(contours)
    controller = GuiController(grabber, detector)
    # pyautogui functions not actually called; test that no exception is raised
    assert controller.click() is True


def test_click_failure(monkeypatch):
    img = np.zeros((10, 10), dtype=np.uint8)
    grabber = DummyGrabber(img)
    # detector returns nothing -> raise
    detector = DummyDetector([])
    controller = GuiController(grabber, detector)
    with pytest.raises(ClickFailure):
        controller.click(retries=1)


def test_click_with_custom_dir(monkeypatch):
    """Ensure click accepts a template directory and uses it."""
    img = np.zeros((10, 10), dtype=np.uint8)
    grabber = DummyGrabber(img)
    controller = GuiController(grabber, DummyDetector([np.array([[[1, 2]]]]) ))

    # patch TemplateDetector so we can see what directory is passed
    seen = []
    class FakeDetector:
        def __init__(self, directory, threshold):
            seen.append(directory)
        def find(self, image):
            return [np.array([[[1, 2]]]])

    monkeypatch.setattr('gui_control.controller.TemplateDetector', FakeDetector)
    assert controller.click(Path("/some/dir")) is True
    assert seen == [Path("/some/dir")]


def test_click_template_helper(monkeypatch):
    """click_template should try multiple locations before falling back."""
    img = np.zeros((10, 10), dtype=np.uint8)
    grabber = DummyGrabber(img)
    controller = GuiController(grabber, DummyDetector([np.array([[[1, 2]]]]) ))

    calls = []
    def fake_click(path, retries=None):
        calls.append(path)
        # pretend first candidate fails, second succeeds
        return 'success' in str(path)

    monkeypatch.setattr(controller, 'click', fake_click)

    result = controller.click_template("foo", template_dirs=["/a", "/b"], retries=2)
    assert result is True
    assert calls[0] == Path("/a/foo")
    assert calls[1] == Path("/b/foo")
    # global fallback appended last
    assert calls[-1] == Path(Config.TEMPLATES_DIR) / "foo"
