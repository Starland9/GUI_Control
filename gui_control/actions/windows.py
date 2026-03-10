import time
from pathlib import Path
import pyautogui
from typing import Iterable, Optional

from ..config import Config
from ..controller import GuiController


class Windows:
    """Component wrapping Windows start‑menu and related UI shortcuts.

    `template_dirs` may be provided so that the component can click
    particular icons (e.g. settings, run dialog) if templates exist for them.
    """

    def __init__(self,
                 controller: GuiController,
                 template_dirs: Optional[Iterable[str]] = None):
        self.controller = controller
        self.template_dirs = list(template_dirs) if template_dirs else []

    def search(self, query: str) -> None:
        """Search for an application or setting via the Windows start menu."""
        pyautogui.press("win")
        time.sleep(Config.WIN_KEY_DELAY)
        pyautogui.typewrite(query, interval=Config.TYPE_DELAY)
        pyautogui.press("enter")
        time.sleep(Config.DEFAULT_WAIT_TIME)

    def open_settings(self) -> None:
        """Open Windows Settings (attempts template, then types "settings")."""
        if self.controller.click_template("settings_icon", template_dirs=self.template_dirs):
            return
        # fallback to keyboard
        self.search("settings")

    def open_run_dialog(self) -> None:
        """Open the Run dialog (Win+R)."""
        pyautogui.hotkey("win", "r")
        time.sleep(Config.DEFAULT_WAIT_TIME)
