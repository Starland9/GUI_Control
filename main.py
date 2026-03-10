import logging

from gui_control.actions.whatsapp import Whatsapp
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

        controller = bot.GuiController(
            grabber=bot.ScreenGrabber(),
            detector=bot.TemplateDetector(
                Config.TEMPLATES_DIR / "whatsapp" / "message_input_field", Config.TEMPLATE_MATCH_THRESHOLD),
        )
        
        whatsapp = Whatsapp(controller, template_dirs=[str(Config.TEMPLATES_DIR / "whatsapp")])
        whatsapp.send_message("John Doe", "Hello from GUI_Control!")

        logging.info("Automatisation terminée avec succès")
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution: {e}")
        raise
