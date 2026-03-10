"""Top-level package for GUI_Control automation library."""

from .config import Config
from .controller import GuiController
from .screenshot import ScreenGrabber
from .detector import TemplateDetector
from .actions.browser import Browser
from .actions.windows import Windows

__all__ = [
    "Config",
    "GuiController",
    "ScreenGrabber",
    "TemplateDetector",
    "Browser",
    "Windows",
]
