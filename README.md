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

### Option 1 : Récupérer les données depuis les APIs (Reddit + Arxiv)

```bash
python app.py
```

Ce script va :
- Récupérer des posts Reddit sur le thème "climate"
- Récupérer des articles Arxiv sur le même thème
- Créer/mettre à jour le fichier `corpus.csv`

### Option 2 : Utiliser le corpus existant

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

## Structure du projet

- `app.py` : Récupération des données depuis Reddit et Arxiv (TD 3)
- `Document.py` : Classes Document, RedditDocument, ArxivDocument (TD 4, TD 5)
- `Author.py` : Classe Author pour gérer les auteurs (TD 4)
- `Corpus.py` : Classe Corpus pour gérer la collection de documents (TD 4, TD 6)
- `MoteurRecherche.py` : Classe MoteurRecherche pour le moteur de recherche (TD 7)
- `DocumentFactory.py` : Factory pattern pour créer des documents (TD 5)
- `corpus.csv` : Fichier de données (généré par app.py)
