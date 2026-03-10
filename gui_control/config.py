import os
from dataclasses import dataclass
from pathlib import Path

# "dotenv" lets us override configuration using a .env file in the project root.
# Add python-dotenv to your requirements if you want to use this feature.
try:
    from dotenv import load_dotenv
except ImportError:  # if python-dotenv isn't installed, just ignore
    def load_dotenv(*args, **kwargs):
        pass

# Base directory of the *project* – config lives inside the package so we
# walk two levels up to reach root.  This is where `.env` and `assets/` live.
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


@dataclass
class Config:
    # Moniteur principal
    MONITOR = {
        "top": int(os.getenv("MONITOR_TOP", 0)),
        "left": int(os.getenv("MONITOR_LEFT", 0)),
        "width": int(os.getenv("MONITOR_WIDTH", 1920 * 2)),
        "height": int(os.getenv("MONITOR_HEIGHT", 1080))
    }

    # Chemins
    BASE_DIR: Path = BASE_DIR
    TEMPLATES_DIR: Path = Path(os.getenv("TEMPLATES_DIR", BASE_DIR / "assets"))

    # Temps d'attente par défaut
    DEFAULT_WAIT_TIME: float = float(os.getenv("DEFAULT_WAIT_TIME", 2))

    # Paramètres de recherche
    BROWSER_SEARCH_URL: str = os.getenv(
        "BROWSER_SEARCH_URL", "https://www.google.com/")
    SEARCH_BAR_TIMEOUT: int = int(os.getenv("SEARCH_BAR_TIMEOUT", 5))

    # Paramètres de détection d'images
    TEMPLATE_MATCH_THRESHOLD: float = float(os.getenv(
        "TEMPLATE_MATCH_THRESHOLD", 0.5))  # Seuil de correspondance pour les templates
    # Nombre maximum de tentatives
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))
    # Délai entre les tentatives (en secondes)
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", 1))

    # Paramètres de mouvement de la souris
    # Durée du mouvement de la souris (en secondes)
    MOUSE_MOVE_DURATION: float = float(os.getenv("MOUSE_MOVE_DURATION", 1))

    # Paramètres de recherche Windows
    # Délai après pression de la touche Windows
    WIN_KEY_DELAY: float = float(os.getenv("WIN_KEY_DELAY", 1))
    # Délai entre les touches lors de la frappe
    TYPE_DELAY: float = float(os.getenv("TYPE_DELAY", 0.1))
