from Document import Document

#Classe Autor pour gérer les auteurs et leurs documents
class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.productions = {}

    def __str__(self):
        return f"Author(name={self.name})"
    
    def __repr__(self):
        return f"Author(name={self.name}, ndoc={self.ndoc}, productions={self.productions})"
    
    # Affichage  dees informations de l'auteur
    def afficher_infos(self):
        """Affiche les informations de l'auteur"""
        print(f"Nom de l'auteur: {self.name}")
        print(f"Nombre de documents: {self.ndoc}")
        print("Productions:")
        for doc_id, doc in self.productions.items():
            print(f"  [{doc_id}] {doc.titre}")
#Ajout d'un document à l'auteur
    def add (self, doc_id, document):
        self.productions[doc_id] = document
        self.ndoc = len(self.productions)

    def get_nombre_documents(self):
        return self.ndoc
    def get_productions(self):
        return self.productions

# Calcul de la taille moyenne des documents de l'auteur
    def get_taille_moyenne_documents(self):
        if self.ndoc == 0:
            return 0
        total_caratere = sum(len(doc.texte) for doc in self.productions.values())
        return total_caratere / self.ndoc
    
