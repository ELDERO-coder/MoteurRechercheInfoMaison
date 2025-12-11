import pandas as pd
import numpy as np
import re
from scipy.sparse import csr_matrix
from Corpus import Corpus

class MoteurRecherche:
    def __init__(self, corpus: Corpus):
        """
        Initialisation du moteur de recherche avec un corpus généré dans corpus.csv
        et construction automatique de la matrice Documents x Termes.
        """
        self.corpus = corpus
        self.vocab = {}          # Dictionnaire du vocabulaire 
        self.mat_TF = None       # Matrice Term Frequency
        self.mat_TFxIDF = None   # Matrice TFxIDF
        self.idf = None          # Vecteur IDF (optionnel)

        # Construction du vocabulaire et des matrices
        self._build_vocabulary()
        self._build_TF_matrix()
        self._build_TFxIDF_matrix()
    
    def nettoyer_text(self, text):
        """Nettoyage du texte du corpus"""
        if not isinstance(text, str):
            text = str(text)
        text = text.lower()
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _build_vocabulary(self):
        """
        Construction du vocabulaire :
        - découper les textes en mots
        - retrait des doublons
        - tri alphabétique
        - stockage de l'id unique, du total d'occurrences, et plus tard df
        """
        all_words = []
        word_to_count = {}  # mot -> nb total d'occurrences
        
        for doc_id, doc in self.corpus.id2doc.items():
            texte_net = self.nettoyer_text(doc.texte)
            mots = re.findall(r'\b\w+\b', texte_net)
            all_words.extend(mots)
            
            for mot in mots:
                word_to_count[mot] = word_to_count.get(mot, 0) + 1
        
        # Mots uniques triés
        mots_uniques = sorted(set(all_words))
        
        # Dictionnaire vocab : mot -> infos
        for idx, mot in enumerate(mots_uniques):
            self.vocab[mot] = {
                'id': idx,
                'total_occurrences': word_to_count[mot],
                'document_frequency': 0
            }
    
    def _build_TF_matrix(self):
        """
        Construction de la matrice TF (Term Frequency)
        Dimensions : nb_docs x nb_mots
        """
        nb_docs = len(self.corpus.id2doc)
        nb_mots = len(self.vocab)
        
        rows = []
        cols = []
        data = []
        
        # Mapping doc_id -> indice de ligne
        doc_ids = sorted(self.corpus.id2doc.keys())
        doc_id_to_index = {doc_id: idx for idx, doc_id in enumerate(doc_ids)}
        
        # Parcours des documents
        for doc_id, doc in self.corpus.id2doc.items():
            doc_idx = doc_id_to_index[doc_id]
            texte_net = self.nettoyer_text(doc.texte)
            mots = re.findall(r'\b\w+\b', texte_net)
            
            word_counts = {}
            for mot in mots:
                if mot in self.vocab:
                    word_counts[mot] = word_counts.get(mot, 0) + 1
            
            for mot, count in word_counts.items():
                word_id = self.vocab[mot]['id']
                rows.append(doc_idx)
                cols.append(word_id)
                data.append(count)  # TF brut = nb d'occurrences dans le doc
        
        # Matrice creuse CSR
        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(nb_docs, nb_mots))

        # Calcul de la document frequency (df) pour chaque mot
        doc_freq = {}  # mot -> nb de docs contenant ce mot
        
        for doc_id, doc in self.corpus.id2doc.items():
            texte_net = self.nettoyer_text(doc.texte)
            mots_doc = set(re.findall(r'\b\w+\b', texte_net))
            for mot in mots_doc:
                if mot in self.vocab:
                    doc_freq[mot] = doc_freq.get(mot, 0) + 1
        
        for mot in self.vocab:
            self.vocab[mot]['document_frequency'] = doc_freq.get(mot, 0)
    
    def _build_TFxIDF_matrix(self):
    
        nb_docs = len(self.corpus.id2doc)
        nb_terms = len(self.vocab)

    # Vecteur IDF
        idf_values = np.zeros(nb_terms, dtype=np.float32)
        for mot, info in self.vocab.items():
            word_id = info['id']
            df = info['document_frequency']
            if df > 0:
                idf_values[word_id] = np.log(nb_docs / df)
            else:
                idf_values[word_id] = 0.0
    
        self.idf = idf_values

    # TF en float32
        self.mat_TF = self.mat_TF.astype(np.float32)

    
        self.mat_TFxIDF = self.mat_TF.multiply(idf_values).tocsr()

    
    def _query_to_vector(self, mots_clefs):
        """
        Transformation des mots-clés de la requête en vecteur dense de taille |vocab|.
        """
        query_clean = self.nettoyer_text(mots_clefs)
        query_words = re.findall(r'\b\w+\b', query_clean)

        vector = np.zeros(len(self.vocab), dtype=np.float32)
        
        for mot in query_words:
            if mot in self.vocab:
                word_id = self.vocab[mot]['id']
                vector[word_id] += 1
        
        return vector
    
    def search(self, mots_clefs, nb_docs=10):
        """
        Fonction de recherche
        
        Arguments:
            - mots_clefs: string contenant les mots-clés de la requête
            - nb_docs: nombre de documents à retourner
        
        Retourne:
            - un DataFrame pandas contenant les résultats de recherche
              (doc_id, titre, auteur, score)
        """
        # Transformer la requête en vecteur
        query_vector = self._query_to_vector(mots_clefs)
        
        # Normalisation du vecteur requête
        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            # Aucun mot de la requête n'est dans le vocabulaire
            return pd.DataFrame(columns=['doc_id', 'titre', 'auteur', 'score'])
        
        query_vector_normalized = query_vector / query_norm
        
        # Matrice TFxIDF
        matrix = self.mat_TFxIDF
        
        from tqdm import tqdm
        
        scores = []
        doc_ids = sorted(self.corpus.id2doc.keys())
        
        for doc_idx, doc_id in enumerate(tqdm(doc_ids, desc="Calcul des scores")):
            # Vecteur document (on densifie UNE ligne à la fois → OK)
            doc_vector = matrix[doc_idx, :].toarray().flatten()
            
            doc_norm = np.linalg.norm(doc_vector)
            if doc_norm > 0:
                doc_vector_normalized = doc_vector / doc_norm
                score = np.dot(query_vector_normalized, doc_vector_normalized)
            else:
                score = 0.0
            
            scores.append({
                'doc_id': doc_id,
                'score': score
            })
        
        # Tri par score décroissant
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # On ne garde que les nb_docs meilleurs
        top_scores = scores[:nb_docs]
        
        # Construction du DataFrame résultats
        results = []
        for result in top_scores:
            doc_id = result['doc_id']
            doc = self.corpus.id2doc[doc_id]
            
            results.append({
                'doc_id': doc_id,
                'titre': doc.titre,
                'auteur': doc.auteur,
                'score': result['score']
            })
        
        df_results = pd.DataFrame(results)
        return df_results
