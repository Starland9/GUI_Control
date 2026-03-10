import time
from typing import Iterable
import pyautogui
from pathlib import Path

from .config import Config
from .screenshot import ScreenGrabber
from .detector import TemplateDetector
from .exceptions import ClickFailure


class GuiController:
    def __init__(self,
                 grabber: ScreenGrabber,
                 detector: TemplateDetector):
        self.grabber = grabber
        self.detector = detector

    def click(self,
              template_dir: Path | None = None,
              retries: int | None = None) -> bool:
        """Click the first object found on screen.

        If ``template_dir`` is supplied we instantiate a throw‑away
        :class:`TemplateDetector` targeting that directory; otherwise the
        controller’s default detector is used.
        """
        retries = retries or Config.MAX_RETRIES
        for attempt in range(retries):
            try:
                img = self.grabber.grab_gray()
                if template_dir is None:
                    contours = self.detector.find(img)
                else:
                    temp = TemplateDetector(template_dir,
                                            Config.TEMPLATE_MATCH_THRESHOLD)
                    contours = temp.find(img)
                x, y = contours[0][0][0]
                pyautogui.moveTo(
                    x + 100, y + 25, duration=Config.MOUSE_MOVE_DURATION)
                pyautogui.leftClick()
                return True
            except Exception as e:
                if attempt == retries - 1:
                    raise ClickFailure(e)
                time.sleep(Config.RETRY_DELAY)
        return False

    def click_template(self,
                       name: str,
                       template_dirs: Iterable[str] | None = None,
                       retries: int | None = None) -> bool:
        """Search for *name* in one of the template directories and click it.

        ``template_dirs`` may contain absolute paths or directory names relative
        to :data:`Config.TEMPLATES_DIR`; the global folder is always tried last.
        """
        candidates: list[Path] = []
        if template_dirs:
            for d in template_dirs:
                base = Path(d)
                candidates.append(base / name if base.is_dir() else base)
                candidates.append(Path(Config.TEMPLATES_DIR) / d / name)
        candidates.append(Path(Config.TEMPLATES_DIR) / name)

        for path in candidates:
            try:
                if self.click(path, retries=retries):
                    return True
            except Exception:
                continue
        return False
