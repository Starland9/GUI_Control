import pytest

from gui_control.actions.windows import Windows
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


def test_windows_search(monkeypatch):
    ctrl = DummyController()
    windows = Windows(ctrl)

    # basic search should not raise
    windows.search("Calculator")
    assert ctrl.clicked == []  # no template clicks


def test_open_settings_via_template(monkeypatch, tmp_path):
    ctrl = DummyController()
    # create fake template dir and file
    d = tmp_path / "tpl"
    d.mkdir()
    (d / "settings_icon").write_text("dummy")
    windows = Windows(ctrl, template_dirs=[str(d)])

    windows.open_settings()
    assert ctrl.clicked, "settings_icon template should be clicked"


def test_open_run_dialog():
    ctrl = DummyController()
    windows = Windows(ctrl)
    # run dialog just triggers a hotkey; ensure no exception
    windows.open_run_dialog()
