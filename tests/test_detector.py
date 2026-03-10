import numpy as np
import pytest

from gui_control.detector import TemplateDetector
from gui_control.exceptions import NoObjectFound
from gui_control.config import Config


def test_detector_raises_on_empty(monkeypatch, tmp_path):
    # empty directory should raise FileNotFoundError or NoObjectFound
    dirpath = tmp_path / "empty"
    dirpath.mkdir()
    detector = TemplateDetector(dirpath, Config.TEMPLATE_MATCH_THRESHOLD)
    # grab a dummy image (all zeros)
    img = np.zeros((100, 100), dtype=np.uint8)
    with pytest.raises(NoObjectFound):
        detector.find(img)
