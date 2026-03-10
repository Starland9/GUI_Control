# GUI Control Automation

Un outil d'automatisation GUI qui utilise la reconnaissance d'images pour interagir avec des éléments de l'interface utilisateur.

## Fonctionnalités

- Recherche automatique sur Google
- Lancement d'applications via la barre de recherche Windows
- Détection d'objets par reconnaissance d'images
- Gestion des erreurs et retry automatique
- Configuration centralisée
- Logging détaillé

## Configuration

La configuration est gérée via `gui_control/config.py` et supporte la surcharge
par des variables d'environnement ou un fichier `.env` (voir `.env.example`).
Les options comprennent :
- Paramètres d'affichage
- Chemins des assets
- Temps d'attente
- Seuils de détection
- Paramètres de mouvement de la souris

## Installation

1. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Assurez-vous d'avoir un dossier `assets` avec les templates d'images nécessaires

## Utilisation

**Via le script d'exemple**

```bash
python main.py
```

**En tant que bibliothèque**

Vous pouvez importer et utiliser les classes directement ; certaines
fonctionnalités sont désormais organisées en **composants** (par ex. le
navigateur) :

```python
from gui_control.logger import setup_logging
from gui_control.config import Config
from gui_control.controller import GuiController
from gui_control.screenshot import ScreenGrabber
from gui_control.detector import TemplateDetector
from gui_control.actions.browser import Browser

setup_logging()

controller = GuiController(
    grabber=ScreenGrabber(),
    detector=TemplateDetector(Config.TEMPLATES_DIR, Config.TEMPLATE_MATCH_THRESHOLD),
)
browser = Browser(controller)

# un composant expose plusieurs opérations
browser.search("Développer en java")

# composant Windows
from gui_control.actions.windows_search import Windows
windows = Windows(controller)
windows.search("Visual Studio Code")

# Contrôleur : on peut cliquer sur un dossier de templates spécifique
controller.click(template_dir=Path("./assets/google_search_bar"))

# on peut également utiliser les helpers du contrôleur pour résoudre les
# templates à partir de plusieurs répertoires
controller.click_template("google_search_bar", template_dirs=["./assets/custom"])

# on peut aussi passer des dossiers de templates personnalisés aux composants
browser = Browser(controller, template_dirs=["./assets/custom"])
browser.search("quelque chose")
browser.new_tab()
browser.bookmark_page()
```

La version précédente (`BrowserSearch`) reste disponible pour compatibilité,
mais le composant `Browser` peut être étendu avec de nouvelles méthodes
(p.ex. ouvrir un onglet, ajouter un favori, rafraîchir la page…).

L’implémentation du contrôleur a évolué :

* ``GuiController.click(template_dir=None, retries=None)`` permet de cliquer
  en spécifiant un répertoire de templates à la volée.
* ``GuiController.click_template(name, template_dirs=None)`` recherche un
  template parmi plusieurs dossiers et clique automatiquement.

Ces helpers sont utilisés en interne par les composants, mais vous pouvez
les appeler directement si vous avez besoin d’une logique personnalisée.

Un autre composant fourni est `Windows` ; il encapsule les actions liées
au menu démarrer et aux raccourcis Windows. Il expose `search`,
`open_settings`, `open_run_dialog` et utilise également ``template_dirs``
comme les autres composants.

Le module `gui_control` expose aussi une interface de haut niveau similaire
à l'ancien script :

```python
import gui_control

gui_control.search_in_browser("Salut")
```

Le script va :
1. Ouvrir votre navigateur par défaut
2. Rechercher "Developper en java" sur Google
3. Lancer Visual Studio Code via la barre de recherche Windows

## Structure du projet

```
GUI_Control/
├── assets/                       # Dossier des templates d'images
├── gui_control/                  # package principal
│   ├── __init__.py
│   ├── config.py                 # configuration loader
│   ├── controller.py             # clics / automatisation générique
│   ├── detector.py               # recherche d'objets par template
│   ├── screenshot.py             # encapsule mss
│   ├── exceptions.py             # erreurs métier
│   ├── logger.py                 # configuration du logging
│   └── actions/                  # comportements spécifiques
│       ├── browser.py            # recherche Google
│       └── windows_search.py     # recherche de logiciel
├── main.py                       # point d'entrée (exemple)
├── requirements.txt              # dépendances Python
├── tests/                        # tests unitaires (pytest)
├── .env.example                  # modèle de configuration
└── automation.log                # fichier de log (généré à l'exécution)
```

## Débogage

Les logs sont enregistrés dans `automation.log` avec un niveau de détail INFO. Vous pouvez ajuster le niveau de log dans [main.py](main.py) en modifiant la configuration du logging.

## Contributing

1. Créez une branche pour vos modifications
2. Commitez vos changements
3. Poussez la branche
4. Créez une Pull Request
