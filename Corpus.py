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
        # Utiliser afficher_infos au lieu de afficher
        auteur.afficher_infos()
        print(f"Taille moyenne des documents : {auteur.get_taille_moyenne_documents():.2f} caractères")

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
                # Gérer les colonnes en majuscules ou minuscules
                doc_type = row.get("type", row.get("Type", "Document"))
                
                # Récupérer les colonnes (essayer majuscules puis minuscules)
                titre = row.get('Titre', row.get('titre', ''))
                auteur = row.get('Auteur', row.get('auteur', ''))
                date = row.get('Date', row.get('date', ''))
                url = row.get('URL', row.get('url', ''))
                texte = row.get('text', row.get('texte', ''))

                if doc_type == "Reddit":
                    obj = RedditDocument(
                        titre, auteur, date,
                        url, texte, nb_commentaires=0
                    )

                elif doc_type == "Arxiv":
                    obj = ArxivDocument(
                        titre, auteur, date,
                        url, texte, coauthors=[]
                    )

                else:
                    obj = Document(
                        titre, auteur, date,
                        url, texte
                    )

                doc_id = row.get("id", row.get("ID", len(corpus.id2doc)))
                corpus.add_document_obj(doc_id, obj)

            return corpus
        
        elif format_type == 'pickle':
            with open(f"{filename}.pkl", 'rb') as f:
                return pickle.load(f)


    def __repr__(self):
        return f"<Corpus '{self.nom}', {self.ndoc} document(s), {self.naut} auteur(s)>"
    

    #La fonction de recherche qui va retourner les passages de document contenant le mot clé
    def search(self, keyword):
        # Construire la chaîne complète une seule fois si pas déjà fait
        if not hasattr(self, '_texte_complet'):
            self._texte_complet = ' '.join([doc.texte for doc in self.id2doc.values()])
        
        results = []
        keyword_lower = keyword.lower()
        for doc_id, doc in self.id2doc.items():
            if keyword_lower in doc.texte.lower() or keyword_lower in doc.titre.lower():
                results.append((doc_id, doc))
        return results
            

#fonction de concordance en utilisant re et pandas et avoir dans un tableau :contexte gauche, motif trouvé, contexte droit
    def concorde(self, keyword, taille=30): 
        concordance_list = []
        # Pattern pour capturer contexte gauche, motif, contexte droit
        pattern = re.compile(
            r'(.{0,' + str(taille) + r'})\b' + re.escape(keyword) + r'\b(.{0,' + str(taille) + r'})',
            re.IGNORECASE
        )

        for doc_id, doc in self.id2doc.items():
            for match in pattern.finditer(doc.texte):
                contexte_gauche = match.group(1).strip()
                motif_trouve = keyword
                contexte_droit = match.group(2).strip()
                
                concordance_list.append({
                    'doc_id': doc_id,
                    'contexte_gauche': contexte_gauche,
                    'motif_trouve': motif_trouve,
                    'contexte_droit': contexte_droit,
                    'concordance': contexte_gauche + ' [' + motif_trouve + '] ' + contexte_droit
                })

        return pd.DataFrame(concordance_list)

#PARTIE 2: Statistiques 

#Fonction nettoyer_text qui prend une chaine de caractères en entrée et lui applique une chaine de traitement, mise en minuscule, remplacement des passages à la ligne

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
    def mots_plus_frequents(self, n=10):
        from collections import Counter
        compteur_mots = Counter()
        for doc_id, doc in self.id2doc.items():
            texte_net = self.nettoyer_text(doc.texte)
            mots = re.findall(r'\b\w+\b', texte_net)
            compteur_mots.update(mots)
        return compteur_mots.most_common(n)

    # Méthode stats complète selon TD6 - affiche statistiques textuelles
    def stats(self, n=10):
        """Affiche les statistiques textuelles du corpus"""
        from collections import Counter
        
        # Compteurs pour term frequency et document frequency
        compteur_tf = Counter()  # Term frequency (nombre total d'occurrences)
        compteur_df = Counter()  # Document frequency (nombre de documents contenant le mot)
        
        vocabulaire = set()
        
        # Parcourir tous les documents une seule fois
        for doc_id, doc in self.id2doc.items():
            # Nettoyer le texte
            texte_net = self.nettoyer_text(doc.texte)
            # Extraire les mots
            mots = re.findall(r'\b\w+\b', texte_net)
            # Mettre à jour le vocabulaire
            vocabulaire.update(mots)
            # Compter les occurrences (term frequency)
            compteur_tf.update(mots)
            # Compter les documents contenant chaque mot unique (document frequency)
            mots_uniques_doc = set(mots)
            compteur_df.update(mots_uniques_doc)
        
        # Créer le DataFrame avec les fréquences
        if vocabulaire:  # Vérifier qu'on a un vocabulaire
            freq_data = []
            for mot in vocabulaire:
                freq_data.append({
                    'mot': mot,
                    'term_frequency': compteur_tf[mot],
                    'document_frequency': compteur_df[mot]
                })
            
            df_freq = pd.DataFrame(freq_data)
            # Trier par term frequency décroissante
            if not df_freq.empty:
                df_freq = df_freq.sort_values('term_frequency', ascending=False)
        else:
            df_freq = pd.DataFrame(columns=['mot', 'term_frequency', 'document_frequency'])
        
        # Afficher les statistiques
        print(f"\n=== Statistiques du corpus '{self.nom}' ===")
        print(f"Nombre de documents : {self.ndoc}")
        print(f"Nombre de mots différents (vocabulaire) : {len(vocabulaire)}")
        print(f"\nLes {n} mots les plus fréquents :")
        print(df_freq.head(n).to_string(index=False))
        
        return df_freq
    
#Dictionnaire vocab contenant le text de mes documents (retirer les doublons et trier par ordre alphabétique)
    def vocab(self):
        vocab = set()
        for doc_id, doc in self.id2doc.items():
            texte_net = self.nettoyer_text(doc.texte)
            mots = re.findall(r'\b\w+\b', texte_net)
            vocab.update(mots)
        return sorted(vocab)
    





