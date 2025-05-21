import logging

from config import Config
import gui_control as bot

if __name__ == "__main__":
    try:
        logging.info("Démarrage de l'automatisation")
        
        # Vérification des dossiers nécessaires
        if not Config.TEMPLATES_DIR.exists():
            raise FileNotFoundError(f"Dossier templates non trouvé: {Config.TEMPLATES_DIR}")
            
        # Exécution des tâches
        bot.search_in_browser("Developper en java")
        bot.search_sofware("Visual Studio Code")
        
        logging.info("Automatisation terminée avec succès")
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution: {e}")
        raise
