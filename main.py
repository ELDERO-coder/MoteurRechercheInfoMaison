import pandas as pd
from Document import Document, RedditDocument, ArxivDocument
from Corpus import Corpus

df = pd.read_csv("corpus.csv")

# Créer un corpus 
corpus = Corpus("Corpus")

for _, row in df.iterrows():

    # Création du type correct selon source reddit ou arxiv
    if row["source"] == "reddit":
        doc = RedditDocument(
            row["titre"],
            row["auteur"],
            row["date"],
            row["url"],
            row["texte"],
            nb_commentaires=0
        )

    elif row["source"] == "arxiv":
        doc = ArxivDocument(
            row["titre"],
            row["auteur"],
            row["date"],
            row["url"],
            row["texte"],
            coauthors=[]
        )

    else:
        
        doc = Document(
            row["titre"],
            row["auteur"],
            row["date"],
            row["url"],
            row["texte"]
        )

    corpus.add_document_obj(row["id"], doc)


# Tests 
print("\n Corpus chargé depuis corpus.csv ===")
print(corpus)

print("\n Tri par date :")
corpus.afficher_tri_date(5)

print("\n Tri par titre :")
corpus.affichier_tri_titre(5)

print("\n Statistiques : ")
corpus.statistiques_auteur(5)
