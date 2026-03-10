import pytest

import pyautogui
from gui_control.actions.browser import Browser
from gui_control.controller import GuiController
from gui_control.screenshot import ScreenGrabber
from gui_control.detector import TemplateDetector
from gui_control.config import Config


class DummyController(GuiController):
    def __init__(self):
        super().__init__(grabber=ScreenGrabber(),
                         detector=TemplateDetector(Config.TEMPLATES_DIR, Config.TEMPLATE_MATCH_THRESHOLD))
        self.clicked = []

    def click(self, *args, **kwargs):
        self.clicked.append((args, kwargs))
        return True


def test_browser_search(monkeypatch, tmp_path):
    controller = DummyController()
    # supply an extra fake template directory to the component
    tmp = tmp_path / "tpl"
    tmp.mkdir()
    (tmp / "google_search_bar").write_text('')
    browser = Browser(controller, template_dirs=[str(tmp)])

    # monkeypatch subprocess.run to avoid opening real browser
    monkeypatch.setattr('subprocess.run', lambda *a, **k: None)

    # calling search should not raise and should click using custom template
    browser.search("test")
    assert controller.clicked, "search should attempt to click something"


def test_browser_shortcuts(monkeypatch):
    controller = DummyController()
    browser = Browser(controller)

    # verify new_tab/bookmark_page don't error
    browser.new_tab()
    browser.bookmark_page()
    # nothing to assert, just ensure no exception
