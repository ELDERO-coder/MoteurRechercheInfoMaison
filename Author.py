from Document import Document
class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.productions = {}

    def add_production(self, document):
        self.productions.append(document)
        self.ndoc += 1

    def __str__(self):
        return f"Author(name={self.name})"
    
    def __repr__(self):
        return f"Author(name={self.name}, ndoc={self.ndoc}, productions={self.productions})"
    def afficher_infos(self):
        print(f"Nom de l'auteur: {self.name}")
        print(f"Nombre de documents: {self.ndoc}")
        print("Productions:")
        for doc in self.productions:
            print(f" - {doc}")

    def add (self, doc_id, document):
        self.productions[doc_id] = document
        self.ndoc = len(self.productions)

    def get_nombre_documents(self):
        return self.ndoc
    def get_productions(self):
        return self.productions
    
    def get_taille_moyenne_documents(self):
        if self.ndoc == 0:
            return 0
        total_caratere = sum(len(doc.texte) for doc in self.productions.values())
        return total_caratere / self.ndoc
    
