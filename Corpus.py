import pandas as pd
import pickle
import json
import re
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
    

    #La fonction de recherhe qui va retourner les passages de document contenant le mot clé
    def search(keyword):
        results = []
        for doc_id, doc in self.id2doc.items():
            if keyword.lower() in doc.texte.lower() or keyword.lower() in doc.titre.lower():
                results.append((doc_id, doc))
        return results
            

#fonction de concordance en utilisant re et panda et avoir dans un tableau :contexte gauche, motivf trouvé, contexte droit
    def concorde (self, keyword, taille =30): 
        concordance_list = []
        pattern = re.compile(r'.{0,' + str(taille) + r'}\b' + re.escape(keyword) + r'\b.{0,' + str(taille) + r'}', re.IGNORECASE)

        for doc_id, doc in self.id2doc.items():
            matches = pattern.findall(doc.texte)
            for match in matches:
                concordance_list.append({
                    'doc_id': doc_id,
                    'concordance': match.strip()
                })

        return pd.DataFrame(concordance_list)

#PARTIE 2: Statistiques 

#Fonction nettoyer_text qui prend une chaine de caractères en entrée et lui applique une chaine de traitement, mise en minuscule, paaasges à la ligne

    def nettoyer_text (self, text):
        text = text.lower()
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
#Le nombre de mots différents dans le corpus

    def nombre_mots_differents (self):
        mots_uniques = set()
        for doc_id, doc in self.id2doc.items():
            mots = re.findall(r'\b\w+\b', doc.texte.lower())
            mots_uniques.update(mots)
        return len(mots_uniques)
    
    #Afficher les n mots les plus fréquents 
    def mots_plus_frequents (self, n=10):
        from collections import Counter
        compteur_mots = Counter()
        for doc_id, doc in self.id2doc.items():
            mots = re.findall(r'\b\w+\b', doc.texte.lower())
            compteur_mots.update(mots)
        return compteur_mots.most_common(n)





