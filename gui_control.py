import pyautogui
import numpy as np
import cv2
from mss import mss
import subprocess
import time
import os
import logging
from pathlib import Path
from config import Config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

monitor = Config.MONITOR


def get_all_files_in_folder(folder):
    """Récupère tous les fichiers dans un dossier avec gestion des erreurs."""
    try:
        folder_path = Path(folder)
        if not folder_path.exists():
            raise FileNotFoundError(f"Dossier non trouvé: {folder}")

        files = [str(file) for file in folder_path.glob('*') if file.is_file()]
        if not files:
            logging.warning(f"Aucun fichier trouvé dans le dossier: {folder}")
        return files
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des fichiers: {e}")
        raise


def templates_by_paths(path):
    """Charge les templates d'images avec gestion des erreurs."""
    try:
        files = get_all_files_in_folder(path)
        templates = []
        for file in files:
            template = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
            if template is None:
                logging.error(f"Impossible de charger le template: {file}")
                continue
            templates.append(template)
        if not templates:
            raise ValueError("Aucun template valide chargé")
        return templates
    except Exception as e:
        logging.error(f"Erreur lors du chargement des templates: {e}")
        raise


def find_object_rect_by_templates(image, path):
    """Trouve les objets correspondant aux templates avec gestion des erreurs."""
    try:
        templates = templates_by_paths(path)
        h, w = image.shape[:2]
        result = np.zeros((h, w), dtype=np.uint8)

        for template in templates:
            res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # Vérification du seuil de correspondance
            if max_val >= Config.TEMPLATE_MATCH_THRESHOLD:
                top_left = max_loc
                bottom_right = (
                    top_left[0] + template.shape[1],
                    top_left[1] + template.shape[0],
                )
                cv2.rectangle(result, top_left, bottom_right, 255, 2)

        contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            logging.warning(f"Aucun objet trouvé avec les templates de: {path}")
        return contours
    except Exception as e:
        logging.error(f"Erreur lors de la détection d'objets: {e}")
        raise


def click_on_object(paths, retries=Config.MAX_RETRIES):
    """Clique sur un objet avec gestion des erreurs et des tentatives multiples."""
    for attempt in range(retries):
        try:
            with mss() as sct:
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                contours = find_object_rect_by_templates(gray, paths)
                if not contours:
                    raise ValueError("Aucun objet trouvé")

                # Utilisation de la première détection
                x, y = contours[0][0][0][0], contours[0][0][0][1]
                pyautogui.moveTo(x + 100, y + 25, duration=Config.MOUSE_MOVE_DURATION)
                pyautogui.leftClick()
                return True

        except Exception as e:
            if attempt == retries - 1:  # Dernière tentative
                logging.error(f"Échec après {retries} tentatives: {e}")
                raise
            else:
                logging.warning(f"Tentative {attempt + 1}/{retries} échouée: {e}")
                time.sleep(Config.RETRY_DELAY)
    return False


def search_in_browser(text):
    """Effectue une recherche sur Google avec gestion des erreurs."""
    try:
        logging.info(f"Recherche de: {text}")
        subprocess.run(["sensible-browser", Config.BROWSER_SEARCH_URL])
        time.sleep(Config.DEFAULT_WAIT_TIME)

        if not click_on_object(Config.TEMPLATES_DIR / "google_search_bar"):
            raise ValueError("Barre de recherche Google non trouvée")

        pyautogui.typewrite(text, interval=Config.TYPE_DELAY)
        pyautogui.press("enter")
        time.sleep(Config.DEFAULT_WAIT_TIME)

        if not click_on_object(Config.TEMPLATES_DIR / "google_search_result"):
            raise ValueError("Résultat de recherche non trouvé")

    except Exception as e:
        logging.error(f"Erreur lors de la recherche Google: {e}")
        raise


def search_sofware(text):
    """Recherche et lance un logiciel via la barre de recherche Windows."""
    try:
        logging.info(f"Recherche de logiciel: {text}")
        pyautogui.press("win")
        time.sleep(Config.WIN_KEY_DELAY)
        pyautogui.typewrite(text, interval=Config.TYPE_DELAY)
        pyautogui.press("enter")
        time.sleep(Config.DEFAULT_WAIT_TIME)
    except Exception as e:
        logging.error(f"Erreur lors de la recherche de logiciel: {e}")
        raise