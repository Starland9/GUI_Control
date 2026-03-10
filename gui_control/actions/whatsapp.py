import time
from pathlib import Path
import pyautogui
from typing import Iterable, Optional

from ..config import Config
from ..controller import GuiController


class Whatsapp:
    """Component wrapping WhatsApp UI shortcuts.

    `template_dirs` may be provided so that the component can click
    particular icons (e.g. settings, chat) if templates exist for them.
    """

    def __init__(self,
                 controller: GuiController,
                 template_dirs: Optional[Iterable[str]] = None):
        self.controller = controller
        self.template_dirs = list(template_dirs) if template_dirs else [
            Config.TEMPLATES_DIR / "whatsapp"]

    def send_message(self, contact: str, message: str) -> None:
        """Send a message to a contact via WhatsApp Web."""
        # This is a very basic implementation; it assumes WhatsApp Web is
        # already open and the contact is visible on the screen.
        if not self.controller.click_template("message_input_field", template_dirs=self.template_dirs):
            raise RuntimeError("message input field template not found")
        time.sleep(Config.DEFAULT_WAIT_TIME)
        pyautogui.typewrite(message, interval=Config.TYPE_DELAY)
        pyautogui.press("enter")
