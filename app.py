import praw
import pandas as pd
import urllib.request
import xmltodict
import os

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
user_agent = os.environ['USER_AGENT']
# ELDEROME
# Dewanou2003#@
reddit = praw.Reddit(client_id= client_id, client_secret= client_secret, user_agent= user_agent)


# Thématique
keyword = "climate"
docs = []
# Recherche dans Reddit
for submission in reddit.subreddit("all").search(keyword, limit=10):
    if submission.selftext:  # Champ contenant le texte
        Auteur= submission.author_fullname if submission.author_fullname else "N/A",
        Titre = submission.title,
        URL = submission.url,
        Date = pd.to_datetime(submission.created_utc, unit='s').date(),
        text = submission.selftext.replace('\n', ' '),
        docs.append([Auteur, Titre, URL, Date, text])


# Requête vers l'API Arxiv
query = "climate"
url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10"

response = urllib.request.urlopen(url)
data = response.read()

# Parsing XML
parsed = xmltodict.parse(data)

# Accès aux entrées
entries = parsed['feed']['entry']
if not isinstance(entries, list):
    entries = [entries]

for entry in entries:
    summary = entry['summary'].replace('\n', ' ')
    docs.append(summary)


# Création du DataFrame
# Exemple de liste de documents récupérés
# docs = [
#     ("Le changement climatique affecte les océans.", "reddit"),
#     ("Climate models predict increased variability.", "arxiv"),
# ]

# Création du DataFrame
df = pd.DataFrame({
    "id": range(len(docs)),
    "Titre": [doc[0] for doc in docs],
    "Auteur": [doc[0] for doc in docs],
    "Date": [doc[0] for doc in docs],
    "URL": [doc[0] for doc in docs],
    "text": [doc[0] for doc in docs],
    "source": [doc[1] for doc in docs],

})


# Sauvegarde sur le disque avec tabulation comme séparateur
df.to_csv("corpus.csv", sep="\t", index=False)


# Chargement du fichier directement en mémoire
df_loaded = pd.read_csv("corpus.csv", sep="\t")

# Affichage pour vérification
print(df_loaded.head())
# Affichage pour vérification
print(df_loaded.head())




# Taille du corpus
print("Nombre de documents :", len(df))

# Calcul du nombre de mots et de phrases
# for i, row in df.iterrows():
#     text = row['text']
#     nb_mots = len(text.split(" "))
#     nb_phrases = len(text.split("."))
#     print(f"Document {row['id']} : {nb_mots} mots, {nb_phrases} phrases")

#Suppression des documents trop courts (moins de 20 caractères)
df_filtrer = df[df['text'].str.len() >= 20]
print("Nombre de documents après filtrage :", len(df_filtrer))

#Une chaine de caratère contenant tous les documents
corpus_texte = " ".join(df_filtrer['text'].tolist())
print("Aperçu du corpus :", corpus_texte[:500], "...")