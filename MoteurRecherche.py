import pandas as pd
import numpy as np
import re
from scipy.sparse import csr_matrix
from Corpus import Corpus

class MoteurRecherche:
    def __init__(self, corpus: Corpus):

        """Initialisation du moteur de recherche avec un corpus généré dans corpus.csv et construiction  automatique de la matrice Documents x Termes."""
        self.corpus = corpus
        self.vocab = {}  # Dictionnaire du vocabulaire 
        self.mat_TF = None  # Matrice Term Frequency à none
        self.mat_TFxIDF = None  # Matrice TFxIDF à none
        
        # Construction du vocabulaire et des matrices
        self._build_vocabulary()
        self._build_TF_matrix()
        self._build_TFxIDF_matrix()
    
    def nettoyer_text(self, text):
        """Nettoyage du texte de Corpus"""
        text = text.lower()
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _build_vocabulary(self):
        """
        Construction du vocabulaire
        - Découper les chaînes en mots
        - Retrait des doublons
        - Tri par ordre alphabétique
        - Stockage de l'id unique et du nombre total d'occurrences
        """
        # Collecte de tous les mots de tous les documents
        all_words = []
        word_to_count = {}  # Compteur des occurrences totales
        
        for doc_id, doc in self.corpus.id2doc.items():
            texte_net = self.nettoyer_text(doc.texte)
            mots = re.findall(r'\b\w+\b', texte_net)
            all_words.extend(mots)
            
            # Compte des occurrences de chaque mot
            for mot in mots:
                word_to_count[mot] = word_to_count.get(mot, 0) + 1
        
        # Création du vocabulaire trié alphabétiquement
        mots_uniques = sorted(set(all_words))
        
        # Construction du dictionnaire vocab avec id unique et nombre d'occurrences
        for idx, mot in enumerate(mots_uniques):
            self.vocab[mot] = {
                'id': idx,
                'total_occurrences': word_to_count[mot],
                'document_frequency': 0  
            }
    
    def _build_TF_matrix(self):
        """ Construction de la matrice TF (Term Frequency) Dimension: Nombre de documents x Nombre de mots"""
        nb_docs = len(self.corpus.id2doc)
        nb_mots = len(self.vocab)
        
        # Liste pour construire la matrice creuse
        rows = []
        cols = []
        data = []
        
        # Création d'un mapping doc_id --- index dans la matrice
        doc_ids = sorted(self.corpus.id2doc.keys())
        doc_id_to_index = {doc_id: idx for idx, doc_id in enumerate(doc_ids)}
        
        # Parcourir tous les documents
        for doc_id, doc in self.corpus.id2doc.items():
            doc_idx = doc_id_to_index[doc_id]
            texte_net = self.nettoyer_text(doc.texte)
            mots = re.findall(r'\b\w+\b', texte_net)
            
            # Compte des occurrences de chaque mot dans ce document
            word_counts = {}
            for mot in mots:
                if mot in self.vocab:
                    word_counts[mot] = word_counts.get(mot, 0) + 1
            
            # Ajout des valeurs dans la matrice
            for mot, count in word_counts.items():
                word_id = self.vocab[mot]['id']
                rows.append(doc_idx)
                cols.append(word_id)
                data.append(count)  # TF = nombre d'occurrences du mot dans le document
        
        # Création de la matrice creuse CSR
        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(nb_docs, nb_mots))
        
        # Calcul de la document frequency pour chaque mot
        # Compte combien de documents contiennent chaque mot
        doc_freq = {}  # mot -> nombre de documents contenant ce mot
        
        for doc_id, doc in self.corpus.id2doc.items():
            texte_net = self.nettoyer_text(doc.texte)
            mots_doc = set(re.findall(r'\b\w+\b', texte_net))
            for mot in mots_doc:
                if mot in self.vocab:
                    doc_freq[mot] = doc_freq.get(mot, 0) + 1
        
        # Mise à jour du vocabulaire avec la document frequency
        for mot in self.vocab:
            self.vocab[mot]['document_frequency'] = doc_freq.get(mot, 0)
    
    def _build_TFxIDF_matrix(self):
        """
        Construction de la matrice TFxIDF
        TFxIDF = TF * IDF où IDF = log(N / df)
        N = nombre total de documents
        df = document frequency (nombre de documents contenant le mot)
        """
        nb_docs = len(self.corpus.id2doc)
        
        # Création de la matrice IDF
        idf_values = np.zeros(len(self.vocab))
        for mot, info in self.vocab.items():
            word_id = info['id']
            df = info['document_frequency']
            if df > 0:
                idf_values[word_id] = np.log(nb_docs / df)
            else:
                idf_values[word_id] = 0
        
        # Multiplication de TF par IDF (élément par élément)
        # Convertir TF en array dense pour la multiplication
        tf_dense = self.mat_TF.toarray()
        idf_matrix = np.tile(idf_values, (nb_docs, 1))
        
        self.mat_TFxIDF = csr_matrix(tf_dense * idf_matrix)
    
    def _query_to_vector(self, mots_clefs):
        """
        Transformation des mots-clés de la requête en vecteur sur le vocabulaire
        Retourne un vecteur sparse avec les fréquences des mots de la requête
        """
        # Nettoyage et extraction des mots de la requête
        query_clean = self.nettoyer_text(mots_clefs)
        query_words = re.findall(r'\b\w+\b', query_clean)
    
    # Création d'un vecteur de taille du vocabulaire
        vector = np.zeros(len(self.vocab))
        
        # Compte des occurrences de chaque mot de la requête
        for mot in query_words:
            if mot in self.vocab:
                word_id = self.vocab[mot]['id']
                vector[word_id] += 1
        
        return vector
    
    def search(self, mots_clefs, nb_docs=10):
        """
        Fonction de recherche
        
        Arguments:
            mots_clefs: string contenant les mots-clés de la requête
            nb_docs: nombre de documents à retourner
        
        Retourne ainsi:
            un DataFrame pandas contenant les résultats de recherche
        """
        # Transformer la requête en vecteur
        query_vector = self._query_to_vector(mots_clefs)
        
        # Normalisation du vecteur requête (pour le cosinus)
        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            # Aucun mot de la requête n'est dans le vocabulaire
            return pd.DataFrame(columns=['doc_id', 'titre', 'auteur', 'score'])
        
        query_vector_normalized = query_vector / query_norm
        
        # Utilisation de la matrice TFxIDF
        matrix = self.mat_TFxIDF
        
        # Calcul de la similarité cosinus entre la requête et tous les documents
        # Similarité cosinus = (A · B) / (||A|| * ||B||)
        from tqdm import tqdm
        
        scores = []
        doc_ids = sorted(self.corpus.id2doc.keys())
        
        for doc_idx, doc_id in enumerate(tqdm(doc_ids, desc="Calcul des scores")):
            # Récupération du vecteur document
            doc_vector = matrix[doc_idx, :].toarray().flatten()
            
            # Calcul de la norme du vecteur document
            doc_norm = np.linalg.norm(doc_vector)
            
            if doc_norm > 0:
                # Normalisation du vecteur document
                doc_vector_normalized = doc_vector / doc_norm
                
                # Produit scalaire (similarité cosinus car les vecteurs sont normalisés pour le cosinus)
                score = np.dot(query_vector_normalized, doc_vector_normalized)
            else:
                score = 0.0
            
            scores.append({
                'doc_id': doc_id,
                'score': score
            })
        
        # Tri par score décroissant
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Garde seulement les nb_docs meilleurs
        top_scores = scores[:nb_docs]
        
        # Construction du DataFrame avec les informations des documents
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

