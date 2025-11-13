import pandas as pd
import pickle
import json
from datetime import datetime

from Document import Document, RedditDocument, ArxivDocument
from Author import Author


class Corpus:
    def __init__(self, nom: str):
        self.nom = nom
        self.authors = {}      
        self.id2doc = {}       #id: Document, RedditDocument, ArxivDocument
        self.ndoc = 0
        self.naut = 0

    def add_document(self, doc_id, titre, auteur, date, url, texte):

        date_obj = datetime.strptime(date, "%Y-%m-%d")

        document = Document(titre, auteur, date_obj, url, texte)
        self.id2doc[doc_id] = document
        self.ndoc += 1

        # Gérer auteur
        if auteur not in self.authors:
            self.authors[auteur] = Author(auteur)
            self.naut += 1

        self.authors[auteur].add(doc_id, document)

    def add_document_obj(self, doc_id, document):
        #Ajoute un objet déjà créé (RedditDocument, ArxivDocument, Document)
        self.id2doc[doc_id] = document
        self.ndoc = len(self.id2doc)

        auteur = document.auteur

        if auteur not in self.authors:
            self.authors[auteur] = Author(auteur)
            self.naut = len(self.authors)

        self.authors[auteur].add(doc_id, document)


    def afficher_tri_date(self, n=5):
        print(f"\n--- {n} premiers documents triés par date ---")
        docs_tries = sorted(
            self.id2doc.items(),
            key=lambda x: x[1].date,
            reverse=True
        )
        for i, (doc_id, doc) in enumerate(docs_tries[:n]):
            print(f"{i+1}. [{doc.type}] {doc.titre} ({doc.date.strftime('%Y-%m-%d')})")

    def affichier_tri_titre(self, n=5):
        print(f"\n--- {n} premiers documents triés par titre ---")
        docs_tries = sorted(
            self.id2doc.items(),
            key=lambda x: x[1].titre.lower()
        )
        for i, (doc_id, doc) in enumerate(docs_tries[:n]):
            print(f"{i+1}. [{doc.type}] {doc.titre}")

    def statistiques_auteur(self, nom_auteur):
        if nom_auteur not in self.authors:
            print(f"Auteur '{nom_auteur}' non trouvé.")
            return
        
        auteur = self.authors[nom_auteur]
        auteur.afficher()

    def to_dataframe(self):
        data = []
        for doc_id, doc in self.id2doc.items():
            data.append({
                'id': doc_id,
                'titre': doc.titre,
                'auteur': doc.auteur,
                'type': doc.type,
                'date': doc.date.strftime("%Y-%m-%d"),
                'url': doc.url,
                'texte': doc.texte,
                'taille_texte': len(doc.texte)
            })
        return pd.DataFrame(data)

    def save(self, filename, format_type='csv'):
        if format_type == 'csv':
            df = self.to_dataframe()
            df.to_csv(f"{filename}.csv", index=False)
            print(f"Corpus sauvegardé dans {filename}.csv")

        elif format_type == 'pickle':
            with open(f"{filename}.pkl", 'wb') as f:
                pickle.dump(self, f)
            print(f"Corpus sauvegardé dans {filename}.pkl")

        elif format_type == "json":
            data = {
                'nom': self.nom,
                'documents': [
                    {
                        'id': doc_id,
                        'titre': doc.titre,
                        'auteur': doc.auteur,
                        'type': doc.type,
                        'date': doc.date.strftime("%Y-%m-%d"),
                        'url': doc.url,
                        'texte': doc.texte
                    }
                    for doc_id, doc in self.id2doc.items()
                ]
            }
            with open(f"{filename}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Corpus sauvegardé dans {filename}.json")


    @classmethod
    def load(cls, filename, format_type='csv'):
        if format_type == 'csv':
            df = pd.read_csv(f"{filename}.csv")
            corpus = cls(f"Corpus_charge_{filename}")

            for _, row in df.iterrows():

                doc_type = row["type"]

                if doc_type == "Reddit":
                    obj = RedditDocument(
                        row['titre'], row['auteur'], row['date'],
                        row['url'], row['texte'], nb_commentaires=0
                    )

                elif doc_type == "Arxiv":
                    obj = ArxivDocument(
                        row['titre'], row['auteur'], row['date'],
                        row['url'], row['texte'], coauthors=[]
                    )

                else:
                    obj = Document(
                        row['titre'], row['auteur'], row['date'],
                        row['url'], row['texte']
                    )

                corpus.add_document_obj(row["id"], obj)

            return corpus
        
        elif format_type == 'pickle':
            with open(f"{filename}.pkl", 'rb') as f:
                return pickle.load(f)


    def __repr__(self):
        return f"<Corpus '{self.nom}', {self.ndoc} document(s), {self.naut} auteur(s)>"
