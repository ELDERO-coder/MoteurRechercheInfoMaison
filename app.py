import praw
import pandas as pd
import urllib.request
import xmltodict
import os

# Thématique
keyword = "climate"
docs = []

# Recherche dans Reddit (optionnel - nécessite les variables d'environnement)
try:
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    user_agent = os.environ['USER_AGENT']
    
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    
    print("Recuperation des donnees Reddit...")
    # Recherche dans Reddit
    for submission in reddit.subreddit("all").search(keyword, limit=10):
        if submission.selftext:  # Champ contenant le texte
            auteur = submission.author.name if submission.author else "N/A"
            titre = submission.title
            url = submission.url
            date = pd.to_datetime(submission.created_utc, unit='s').strftime('%Y-%m-%d')
            texte = submission.selftext.replace('\n', ' ')
            docs.append({
                'titre': titre,
                'auteur': auteur,
                'date': date,
                'url': url,
                'texte': texte,
                'source': 'reddit'
            })
    nb_reddit = len([d for d in docs if d.get('source') == 'reddit'])
    print(f"OK: {nb_reddit} documents Reddit recuperes")
    
except KeyError:
    print("Variables d'environnement Reddit non configurees (CLIENT_ID, CLIENT_SECRET, USER_AGENT)")
    print("  On recupere uniquement les donnees Arxiv (pas besoin d'authentification)")
except Exception as e:
    print(f"Erreur lors de la recuperation Reddit: {e}")
    print("  On continue avec Arxiv seulement")


# Requête vers l'API Arxiv (pas besoin d'authentification)
print("\nRecuperation des donnees Arxiv...")
query = "climate"
url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10"

try:
    response = urllib.request.urlopen(url)
    data = response.read()

    # Parsing XML
    parsed = xmltodict.parse(data)

    # Accès aux entrées
    entries = parsed['feed']['entry']
    if not isinstance(entries, list):
        entries = [entries]

    # Récupération des données Arxiv (corriger les champs manquants)
    for entry in entries:
        titre = entry.get('title', 'Sans titre').replace('\n', ' ').strip()
        # L'auteur peut être un dict ou une liste
        auteurs = entry.get('author', [])
        if isinstance(auteurs, dict):
            auteur = auteurs.get('name', 'Auteur inconnu')
        elif isinstance(auteurs, list):
            auteur = auteurs[0].get('name', 'Auteur inconnu') if auteurs else 'Auteur inconnu'
        else:
            auteur = 'Auteur inconnu'
        
        # Récupérer la date de publication
        date_published = entry.get('published', '')
        if date_published:
            date_obj = pd.to_datetime(date_published)
            date = date_obj.strftime('%Y-%m-%d')
        else:
            date = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        url_arxiv = entry.get('id', '')
        texte = entry.get('summary', '').replace('\n', ' ').strip()
        
        docs.append({
            'titre': titre,
            'auteur': auteur,
            'date': date,
            'url': url_arxiv,
            'texte': texte,
            'source': 'arxiv'
        })
    
    
    nb_arxiv = len([d for d in docs if d.get('source') == 'arxiv'])
    print(f"OK: {nb_arxiv} documents Arxiv recuperes")
    
except Exception as e:
    print(f"Erreur lors de la recuperation Arxiv: {e}")


# Creation du DataFrame avec les donnees recuperees
if not docs:
    print("\nERREUR: Aucun document recupere! Verifiez votre connexion internet ou vos cles Reddit.")
    exit(1)

print(f"\nCréation du DataFrame avec {len(docs)} documents.")
# On crée le DataFrame directement depuis la liste de dictionnaires
df = pd.DataFrame(docs)
df.insert(0, 'id', range(len(docs)))
# Renommer les colonnes pour correspondre au format attendu
df.rename(columns={
    'titre': 'Titre',
    'auteur': 'Auteur',
    'date': 'Date',
    'url': 'URL',
    'texte': 'text'
}, inplace=True)


# Sauvegarde sur le disque avec tabulation comme séparateur
df.to_csv("corpus.csv", sep="\t", index=False)
print(f"OK: Corpus sauvegarde dans corpus.csv ({len(df)} documents)")

# Chargement du fichier directement en memoire pour verification
df_loaded = pd.read_csv("corpus.csv", sep="\t")

print("\nApercu du corpus cree :")
print(df_loaded.head())




# Statistiques du corpus
print(f"\nStatistiques du corpus :")
print(f"   Nombre de documents total : {len(df)}")
print(f"   Sources : Reddit={len(df[df['source']=='reddit'])}, Arxiv={len(df[df['source']=='arxiv'])}")

# Suppression des documents trop courts (moins de 20 caracteres)
df_filtrer = df[df['text'].str.len() >= 20]
print(f"   Documents apres filtrage (>20 caracteres) : {len(df_filtrer)}")

if len(df_filtrer) > 0:
    # Une chaine de caractere contenant tous les documents
    corpus_texte = " ".join(df_filtrer['text'].tolist())
    print(f"\nApercu du corpus (500 premiers caracteres) :")
    print("   " + corpus_texte[:500] + "...")
    
print("\nSUCCES: Corpus cree avec succes! Vous pouvez maintenant lancer 'python main.py'")