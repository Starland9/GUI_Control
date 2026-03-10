import subprocess
import time
from pathlib import Path
from typing import Iterable

import pyautogui

from ..config import Config
from ..controller import GuiController


class Browser:
    """Represents a generic browser that can perform several UI actions.

    The implementation uses templates from the assets directory; consumers may
    subclass or monkey‑patch to add new behaviours.  By default it assumes
    Google Search templates are available under `assets/google_search_*`.
    """

    def __init__(self,
                 controller: GuiController,
                 base_url: str = Config.BROWSER_SEARCH_URL,
                 template_dirs: Iterable[str] | None = None):
        self.controller = controller
        self.base_url = base_url
        self.template_dirs = template_dirs or []

    def _open(self) -> None:
        """Launch the browser pointing at the base URL."""
        subprocess.run(["sensible-browser", self.base_url])
        time.sleep(Config.DEFAULT_WAIT_TIME)

    def search(self, query: str) -> None:
        """Perform a web search similar to the old `BrowserSearch` behaviour."""
        self._open()
        # click the search bar
        if not self.controller.click_template(
                "google_search_bar", template_dirs=self.template_dirs):
            raise RuntimeError("search bar template not found")
        pyautogui.typewrite(query, interval=Config.TYPE_DELAY)
        pyautogui.press("enter")

    # example of additional browser-related methods ------------------------------------------------

    def new_tab(self) -> None:
        """Opens a new browser tab using the standard shortcut.

        This is a trivial example; an implementation could also rely on
        templates for the "new tab" button instead.
        """
        pyautogui.hotkey("ctrl", "t")
        time.sleep(Config.DEFAULT_WAIT_TIME)

    def bookmark_page(self) -> None:
        """Bookmarks the current page (Ctrl‑D shortcut)."""
        pyautogui.hotkey("ctrl", "d")
        time.sleep(Config.DEFAULT_WAIT_TIME)

    def open_url(self, url: str) -> None:
        """Opens the specified URL in the browser."""
        subprocess.run(["sensible-browser", url])
        time.sleep(Config.DEFAULT_WAIT_TIME)

    def select_search_result(self) -> None:
        """Selects a search result"""
        self.controller.click_template(
            "google_search_result", template_dirs=self.template_dirs)
        time.sleep(Config.DEFAULT_WAIT_TIME)

    def _scroll(self, clicks: int, delay: float = 0, times: int = 1) -> None:
        """Scroll the mouse wheel a given number of clicks."""
        for _ in range(times):
            pyautogui.scroll(clicks)
            if delay > 0:
                time.sleep(delay)

        time.sleep(Config.DEFAULT_WAIT_TIME)

    def scroll_down(self, clicks: int = 100, delay: float = 0, times: int = 1) -> None:
        """Scroll down by a given number of clicks."""
        self._scroll(-clicks, delay=delay, times=times)

    def scroll_up(self, clicks: int = 100, delay: float = 0, times: int = 1) -> None:
        """Scroll up by a given number of clicks."""
        self._scroll(clicks, delay=delay, times=times)
