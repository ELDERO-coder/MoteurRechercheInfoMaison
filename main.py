import pandas as pd
from Document import Document, RedditDocument, ArxivDocument
from Corpus import Corpus

df = pd.read_csv("corpus.csv", sep=",")

# Créer un corpus 
corpus = Corpus("Corpus")

for _, row in df.iterrows():

    # Création du type correct selon source reddit ou arxiv
    # Gérer les colonnes en majuscules ou minuscules selon le format du CSV
    source = str(row.get("source", row.get("Source", ""))).lower()
    
    # Récupérer les colonnes (essayer majuscules puis minuscules)
    titre = row.get('Titre', row.get('titre', 'Sans titre'))
    auteur = row.get('Auteur', row.get('auteur', 'Auteur inconnu'))
    date = row.get('Date', row.get('date', ''))
    url = row.get('URL', row.get('url', ''))
    texte = row.get('text', row.get('texte', row.get('text', '')))
    
    # Gérer les cas où les données sont des tuples (ancien format bugué)
    if isinstance(titre, tuple):
        titre = str(titre[0]) if titre and len(titre) > 0 else 'Sans titre'
    if isinstance(auteur, tuple):
        auteur = str(auteur[0]) if auteur and len(auteur) > 0 else 'Auteur inconnu'
    if isinstance(date, tuple):
        date = str(date[0]) if date and len(date) > 0 else ''
    if isinstance(url, tuple):
        url = str(url[0]) if url and len(url) > 0 else ''
    if isinstance(texte, tuple):
        texte = str(texte[0]) if texte and len(texte) > 0 else ''
    
    # Filtrer les documents vides ou corrompus (texte trop court)
    if not texte or len(str(texte)) < 10:
        continue  # Passer ce document si le texte est vide ou trop court
    
    if source == "reddit":
        doc = RedditDocument(
            titre,
            auteur,
            date,
            url,
            texte,
            nb_commentaires=0
        )

    elif source == "arxiv":
        doc = ArxivDocument(
            titre,
            auteur,
            date,
            url,
            texte,
            coauthors=[]
        )

    else:
        # Document générique si source inconnue
        doc = Document(
            titre,
            auteur,
            date,
            url,
            texte
        )

    doc_id = row.get("id", row.get("ID", len(corpus.id2doc)))
    corpus.add_document_obj(doc_id, doc)


# Tests 
print("\n Corpus chargé depuis corpus.csv ===")
print(corpus)

print("\n Tri par date :")
corpus.afficher_tri_date(5)

print("\n Tri par titre :")
corpus.affichier_tri_titre(5)

print("\n Statistiques auteur (premier auteur trouvé) : ")
if corpus.authors:
    premier_auteur = list(corpus.authors.keys())[0]
    corpus.statistiques_auteur(premier_auteur)

print("\n Statistiques du corpus : ")
corpus.stats(10)
