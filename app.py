import praw
import pandas as pd
import urllib.request
import xmltodict
from datetime import datetime
reddit = praw.Reddit(
    client_id='g0yGjEVRBuR3QgQr4bSHRw',
    client_secret='6BHtjRDAR1MrL6xe1jWhUA3N3FQdwQ',
    user_agent='Python WebScraping'
)

keyword = "climate"  # mot-clé de recherche
ids = []
titres = []
auteurs = []
dates = []
urls = []
textes = []
sources = []

doc_id = 0

print("Récupération Reddit…")

for post in reddit.subreddit("all").search(keyword,
limit=10):

    if not post.selftext:  # ignorer posts sans texte
        continue
    texte = post.selftext.replace("\n", " ")

    # auteur = inconnu si None
    auteur = str(post.author) if post.author else "inconnu"

    ids.append(doc_id)
    titres.append(post.title)
    auteurs.append(auteur)
    dates.append(datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d"))
    urls.append(post.url)
    textes.append(texte)
    sources.append("reddit")
    doc_id += 1

print(f"→ {sum(1 for s
in sources if s == 'reddit')} documents Reddit récupérés.")

print("Récupération Arxiv…")

url = f"http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results=10"
response = urllib.request.urlopen(url)

data = response.read()
parsed = xmltodict.parse(data)
entries = parsed["feed"]["entry"]

if not isinstance(entries, list):
    entries = [entries]   # 1 seul résultat possible

for entry in entries:

    summary = entry["summary"].replace("\n", "")
    titre = entry["title"]
    pdf_url = entry["id"]
    date_pub = entry["published"][:10]  # format YYYY-MM-DD
    author_field = entry.get("author", None)

    if author_field is None:
        auteur = "inconnu"

    elif isinstance(author_field, list):  # plusieurs auteurs

        auteur = ", ".join(a["name"] for a
in author_field)

    else:  # un seul auteur
        auteur = author_field["name"]

    # Ajouter au DataFrame 
    ids.append(doc_id)
    titres.append(titre)
    auteurs.append(auteur)
    dates.append(date_pub)
    urls.append(pdf_url)
    textes.append(summary)
    sources.append("arxiv")

    doc_id += 1

print(f"→ {sum(1 for s
in sources if s == 'arxiv')} documents Arxiv récupérés.")

df = pd.DataFrame({
    "id": ids,
    "titre": titres,
    "auteur": auteurs,
    "date": dates,
    "url": urls,
    "texte": textes,
    "source": sources
})

df.to_csv("corpus.csv", index=False)
print("\n Fichier corpus.csv sauvegardé avec succès !")

print("\n=== TAILLE DU CORPUS ===")

print("Nombre de documents :", len(df))

print("\n===== NOMBRE DE MOTS ET PHRASES =====")

for _, row in df.iterrows():
    mots = len(row["texte"].split())
    phrases = len(row["texte"].split("."))
    print(f"Doc {row['id']}: {mots} mots, {phrases} phrases")

print("\n=== SUPPRESSION DOCS < 20 CARACTERES ===")
df_clean = df[df["texte"].str.len() >=
20]
print("Documents conservés :", len(df_clean))







print("\n===== CREATION CHAINE TOTALE =====")

big_string = " ".join(df_clean["texte"])

print("Début de la chaîne :", big_string[:200], "...")