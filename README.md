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

La configuration est gérée via le fichier [config.py](config.py) qui contient :
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

Exécutez le script principal :
```bash
python main.py
```

Le script va :
1. Ouvrir votre navigateur par défaut
2. Rechercher "Developper en java" sur Google
3. Lancer Visual Studio Code via la barre de recherche Windows

## Structure du projet

```
GUI_Control/
├── assets/              # Dossier des templates d'images
├── config.py           # Configuration du projet
├── main.py             # Point d'entrée du programme
├── requirements.txt    # Dépendances Python
├── script.html         # Interface utilisateur (si implémentée)
├── test.py             # Tests unitaires
└── automation.log      # Fichier de log
```

## Débogage

Les logs sont enregistrés dans `automation.log` avec un niveau de détail INFO. Vous pouvez ajuster le niveau de log dans [main.py](main.py) en modifiant la configuration du logging.

## Contributing

1. Créez une branche pour vos modifications
2. Commitez vos changements
3. Poussez la branche
4. Créez une Pull Request
