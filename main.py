import logging

from gui_control.logger import setup_logging
import gui_control as bot
from gui_control.config import Config

from gui_control.actions import *  # noqa: F401, F403

setup_logging()

if __name__ == "__main__":
    try:
        logging.info("Démarrage de l'automatisation")

        # Vérification des dossiers nécessaires
        if not Config.TEMPLATES_DIR.exists():
            raise FileNotFoundError(
                f"Dossier templates non trouvé: {Config.TEMPLATES_DIR}")

        # Exécution des tâches via les composants modernes
        from gui_control.actions.browser import Browser
        from gui_control.actions.windows import Windows

        controller = bot.GuiController(
            grabber=bot.ScreenGrabber(),
            detector=bot.TemplateDetector(
                Config.TEMPLATES_DIR, Config.TEMPLATE_MATCH_THRESHOLD),
        )
        browser = Browser(controller)
        windows = Windows(controller)

        browser._open()
        windows.search("Visual Studio Code")

        # exemples d'extensions de la classe Browser
        browser.new_tab()
        browser.bookmark_page()

        logging.info("Automatisation terminée avec succès")
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution: {e}")
        raise
