from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

import cv2
import numpy as np

from .exceptions import NoObjectFound

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Match – résultat d'une détection
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Match:
    """Represents a single template‑match hit on screen."""
    x: int
    y: int
    w: int
    h: int
    score: float  # TM_CCOEFF_NORMED value in [0, 1]

    @property
    def center_x(self) -> int:
        return self.x + self.w // 2

    @property
    def center_y(self) -> int:
        return self.y + self.h // 2

    def __str__(self) -> str:
        return f"Match(center=({self.center_x},{self.center_y}), score={self.score:.3f})"


# ---------------------------------------------------------------------------
# TemplateDetector
# ---------------------------------------------------------------------------

class TemplateDetector:
    """Multi‑scale, contrast‑enhanced template detector.

    Key improvements over the previous implementation:
    - Templates are stored as a *list* (not a generator) so ``find()`` can be
      called repeatedly.
    - Before matching, the screenshot is enhanced with CLAHE + light Gaussian
      blur to compensate for brightness / gamma differences between the
      captured screen and the reference templates.
    - Multi‑scale matching tries several scale factors so that small DPI /
      zoom differences do not prevent detection.
    - Returns :class:`Match` objects sorted by confidence (highest first).
    """

    # Scales tried for each template; 1.0 is always tried (original size).
    SCALES: tuple[float, ...] = (0.8, 0.9, 1.0, 1.1, 1.2)

    def __init__(
        self,
        templates_dir: Path,
        threshold: float,
        *,
        multi_scale: bool = True,
    ) -> None:
        self.templates_dir = Path(templates_dir)
        self.threshold = threshold
        self.multi_scale = multi_scale
        self._templates: list[tuple[np.ndarray, str]] = self._load_templates()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_templates(self) -> list[tuple[np.ndarray, str]]:
        """Load all valid images from *templates_dir* into a plain list."""
        if not self.templates_dir.exists():
            raise FileNotFoundError(
                f"Templates dir not found: {self.templates_dir}"
            )

        templates: list[tuple[np.ndarray, str]] = []
        for path in sorted(self.templates_dir.iterdir()):
            if not path.is_file():
                continue
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                logger.warning("Could not load template: %s", path.name)
                continue
            templates.append((img, path.name))
            logger.debug("Loaded template %s (%dx%d)", path.name, img.shape[1], img.shape[0])

        if not templates:
            raise ValueError(f"No valid templates in: {self.templates_dir}")

        return templates

    @staticmethod
    def _preprocess(image: np.ndarray) -> np.ndarray:
        """CLAHE contrast normalisation + light Gaussian denoise.

        This dramatically improves matching when the screen brightness or
        colour profile differs from the reference templates.
        """
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        return cv2.GaussianBlur(enhanced, (3, 3), 0)

    def _match_template(
        self, image: np.ndarray, template: np.ndarray
    ) -> Match | None:
        """Return the best :class:`Match` for a single template across all
        scales, or *None* if none exceeds the threshold."""
        scales = self.SCALES if self.multi_scale else (1.0,)
        best: Match | None = None

        for scale in scales:
            if scale == 1.0:
                tpl = template
            else:
                new_w = max(1, int(template.shape[1] * scale))
                new_h = max(1, int(template.shape[0] * scale))
                tpl = cv2.resize(template, (new_w, new_h),
                                 interpolation=cv2.INTER_AREA)

            # Skip if (resized) template is larger than the screenshot
            if tpl.shape[0] >= image.shape[0] or tpl.shape[1] >= image.shape[1]:
                continue

            res = cv2.matchTemplate(image, tpl, cv2.TM_CCOEFF_NORMED)
            _, maxv, _, maxloc = cv2.minMaxLoc(res)

            if maxv >= self.threshold:
                m = Match(
                    x=maxloc[0],
                    y=maxloc[1],
                    w=tpl.shape[1],
                    h=tpl.shape[0],
                    score=round(float(maxv), 4),
                )
                if best is None or m.score > best.score:
                    best = m

        return best

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find(self, image: np.ndarray) -> list[Match]:
        """Detect all templates in *image*.

        Returns a list of :class:`Match` objects sorted by confidence
        (highest first).  Raises :class:`NoObjectFound` when nothing is
        detected above the configured threshold.
        """
        if not self._templates:
            raise NoObjectFound("no templates loaded")

        processed = self._preprocess(image)
        matches: list[Match] = []

        for tpl, name in self._templates:
            m = self._match_template(processed, tpl)
            if m:
                logger.debug("Template '%s' matched at %s", name, m)
                matches.append(m)

        if not matches:
            raise NoObjectFound("no object detected above threshold")

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    def find_best(self, image: np.ndarray) -> Match:
        """Convenience wrapper that returns only the highest‑confidence match."""
        return self.find(image)[0]
