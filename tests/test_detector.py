import numpy as np
import pytest
import cv2

from gui_control.detector import TemplateDetector, Match
from gui_control.exceptions import NoObjectFound
from gui_control.config import Config


def _make_template_dir(tmp_path, tpl_img):
    """Helper: write a grayscale template image into a tmp dir."""
    d = tmp_path / "templates"
    d.mkdir()
    cv2.imwrite(str(d / "btn.png"), tpl_img)
    return d


def test_match_center():
    m = Match(x=10, y=20, w=30, h=40, score=0.95)
    assert m.center_x == 25
    assert m.center_y == 40


def test_find_raises_on_empty_dir(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    with pytest.raises((ValueError, FileNotFoundError)):
        TemplateDetector(d, threshold=0.5)


def test_find_detects_exact_template(tmp_path):
    # create a known pattern and embed it inside a bigger image
    tpl = np.zeros((20, 20), dtype=np.uint8)
    cv2.rectangle(tpl, (2, 2), (18, 18), 255, -1)

    screen = np.zeros((100, 100), dtype=np.uint8)
    screen[30:50, 40:60] = tpl  # paste template at (40,30)

    d = _make_template_dir(tmp_path, tpl)
    detector = TemplateDetector(d, threshold=0.8, multi_scale=False)
    matches = detector.find(screen)

    assert matches, "should find at least one match"
    assert isinstance(matches[0], Match)
    assert matches[0].score >= 0.8


def test_find_best_returns_top_match(tmp_path):
    tpl = np.full((10, 10), 200, dtype=np.uint8)
    screen = np.zeros((80, 80), dtype=np.uint8)
    screen[10:20, 10:20] = tpl

    d = _make_template_dir(tmp_path, tpl)
    detector = TemplateDetector(d, threshold=0.7, multi_scale=False)
    best = detector.find_best(screen)
    assert isinstance(best, Match)


def test_templates_loaded_as_list_not_generator(tmp_path):
    # Critical: templates must survive multiple find() calls
    tpl = np.full((10, 10), 200, dtype=np.uint8)
    screen = np.zeros((80, 80), dtype=np.uint8)
    screen[10:20, 10:20] = tpl

    d = _make_template_dir(tmp_path, tpl)
    detector = TemplateDetector(d, threshold=0.7, multi_scale=False)

    # call find() twice — a generator would fail on the second call
    matches1 = detector.find(screen)
    matches2 = detector.find(screen)
    assert len(matches1) == len(matches2), "templates exhausted after first call!"


def test_find_raises_no_object_found_when_nothing_matches(tmp_path):
    tpl = np.full((10, 10), 200, dtype=np.uint8)
    screen = np.zeros((80, 80), dtype=np.uint8)  # black screen — won't match

    d = _make_template_dir(tmp_path, tpl)
    detector = TemplateDetector(d, threshold=0.99, multi_scale=False)
    with pytest.raises(NoObjectFound):
        detector.find(screen)
