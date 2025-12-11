# Projet TP Python - Moteur de recherche d'information

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration (pour récupérer les données)

Si vous voulez récupérer les données depuis Reddit et Arxiv, configurez les variables d'environnement :

**Windows PowerShell :**
```powershell
$env:CLIENT_ID="votre_client_id"
$env:CLIENT_SECRET="votre_client_secret"
$env:USER_AGENT="votre_user_agent"
```

**Windows CMD :**
```cmd
set CLIENT_ID=votre_client_id
set CLIENT_SECRET=votre_client_secret
set USER_AGENT=votre_user_agent
```

**Linux/Mac :**
```bash
export CLIENT_ID="votre_client_id"
export CLIENT_SECRET="votre_client_secret"
export USER_AGENT="votre_user_agent"
```

## Utilisation

### Opt1: Récupérer les données depuis les APIs (Reddit + Arxiv)

```bash
python app.py
```

Ce script va :
- Récupérer des posts Reddit sur le thème "climate"
- Récupérer des articles Arxiv sur le même thème
- Créer/mettre à jour le fichier `corpus.csv`

### Option2 : Utiliser le corpus existant

Si vous avez déjà un fichier `corpus.csv`, lancez simplement :

```bash
python main.py
```

Ce script va :
- Charger le corpus depuis `corpus.csv`
- Afficher les documents triés par date
- Afficher les documents triés par titre
- Afficher les statistiques d'un auteur
- Afficher les statistiques complètes du corpus (vocabulaire, mots les plus fréquents)

### Opt 3 : Utiliser le notebook Jupyter (TD 8)

Pour le TD 8 qui nécessite une interface avec Jupyter Notebook :

```bash
jupyter notebook TD8.ipynb
```

Le notebook `TD8.ipynb` contient :
- **Partie 1** : Chargement du CSV `discours_US.csv`, création d'un corpus avec découpage en phrases, tests avec `search` et `concorde`
- **Partie 2** : Utilisation du moteur de recherche avec `MoteurRecherche` (incluant la progression avec `tqdm`)
- **Partie 3** : Interface graphique avec widgets Jupyter (recherche interactive, filtres par auteur)

Le notebook utilise le fichier `discours_US.csv` fourni dans le TD 8

### Option 4 : Interface comparative (TD 9-10)

Pour comparer Reddit vs Arxiv et suivre l'évolution temporelle de mots :

```bash
jupyter notebook TD9.ipynb
```

Le notebook `TD9.ipynb` contient :
- Comparaison de fréquence des mots entre deux sources (TF)
- Visualisation temporelle (agrégation mensuelle / trimestrielle / annuelle)
- Interface widgets pour saisir les mots, choisir deux sources et afficher tableau + graphique

### Structure du projet

## Python : 3.12.4

### VERSIONS DU PROJET : 
## — v1 : version qui correspond aux TDs 3 - 5 (socle de base de l’application)
    - `app.py` : Récupération des données depuis Reddit et Arxiv (TD 3)
    - `Document.py` : Classes Document, RedditDocument, ArxivDocument (TD 4, TD 5)
    - `Author.py` : Classe Author pour gérer les auteurs (TD 4)
## — v2 : version qui correspond aux TDs 3 - 7 (avec le moteur de recherche)
    - `Corpus.py` : Classe Corpus avec méthodes de nettoyage, statistiques, recherche (TD 6, TD 7)
    - `MoteurRecherche.py` : Classe MoteurRecherche pour gérer les requêtes (TD 7)
## — v3 : version qui correspond aux TDs 3 - 7 + TD 8 `a 10 (avec l’interface et l’extension)
    - `TD8.ipynb` : Notebook Jupyter pour le TD 8 avec interface graphique
    - `TD9.ipynb` : Notebook Jupyter pour comparaison de corpus et timeline
    - `corpus.csv` : Fichier de données (généré par app.py)
    - `discours_US.csv` : Fichier de données pour le TD 8 (discours politiques )






### MEMBRES DU GROUPE
- Roméo ELOHOUNKPON
- Le Thi Quynh

