import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    # Moniteur principal
    MONITOR = {
        "top": 0,
        "left": 0,
        "width": 1920 * 2,
        "height": 1080
    }
    
    # Chemins
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    TEMPLATES_DIR = BASE_DIR / "assets"
    
    # Temps d'attente par défaut
    DEFAULT_WAIT_TIME = 2
    
    # Paramètres de recherche
    BROWSER_SEARCH_URL = "https://www.google.com/"
    SEARCH_BAR_TIMEOUT = 5
    
    # Paramètres de détection d'images
    TEMPLATE_MATCH_THRESHOLD = 0.5  # Seuil de correspondance pour les templates
    MAX_RETRIES = 3  # Nombre maximum de tentatives
    RETRY_DELAY = 1  # Délai entre les tentatives (en secondes)
    
    # Paramètres de mouvement de la souris
    MOUSE_MOVE_DURATION = 1  # Durée du mouvement de la souris (en secondes)
    
    # Paramètres de recherche Windows
    WIN_KEY_DELAY = 1  # Délai après pression de la touche Windows
    TYPE_DELAY = 0.1  # Délai entre les touches lors de la frappe
