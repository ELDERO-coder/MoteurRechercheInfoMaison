from datetime import datetime

class Document:
    def __init__(self, titre, auteur, date_str, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = self.convertir_date(date_str)
        self.url = url
        self.texte = texte
        self.type = "Document"  # Type par défaut pour les documents génériques

    def convertir_date(self, date_str):
        """Convertit différents formats de date -> datetime, sinon utilise date actuelle."""
        if not date_str:
            return datetime.now()
        
        date_str = str(date_str).strip()
        
        # On essaie  différents formats  de date
        formats = [
            "%Y-%m-%d",           # 2025-11-01
            "%B %d, %Y",          # Novembre 01, 2025
            "%d/%m/%Y",           # 01/11/2025
            "%Y/%m/%d",           # 2025/11/01
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Si aucun format ne fonctionne, ca essai avec dateutil si disponible
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except Exception:
            print(f"Format de date invalide: {date_str}. Utilisation de la date actuelle.")
            return datetime.now()

    def afficher_infos(self):
        """Affiche toutes les informations de l'instance"""
        print("Titre :", self.titre)
        print("Auteur :", self.auteur)
        print("Date :", self.date.strftime("%Y-%m-%d"))
        print("URL :", self.url)
        print("Texte :", self.texte)

    def getType(self):
        """Retourne le type du document"""
        return self.type

    def __str__(self):
        """Version digeste lors d'un print()"""
        return f"Document : {self.titre}"

# Reddit
class RedditDocument(Document):
    def __init__(self, titre, auteur, date_str, url, texte, nb_commentaires):
        super().__init__(titre, auteur, date_str, url, texte)

        self.nb_commentaires = nb_commentaires

        self.type = "Reddit"

    def getType(self):
        """Retourne le type du document"""
        return self.type

    def getNbCommentaires(self):
        return self.nb_commentaires

    def setNbCommentaires(self, nb):
        self.nb_commentaires = nb

    def __str__(self):
        return f"[Reddit] {self.titre} - {self.nb_commentaires} commentaires"
    

# Arxiv
class ArxivDocument(Document):
    def __init__(self, titre, auteur, date_str, url, texte, coauthors):

        super().__init__(titre, auteur, date_str, url, texte)

        self.coauthors = coauthors  # liste de noms des auteur

        self.type = "Arxiv"

    def getType(self):
        """Retourne le type du document"""
        return self.type

    def getCoauthors(self):
        return self.coauthors

    def setCoauthors(self, liste):
        self.coauthors = liste

    def __str__(self):
        liste = ", ".join(self.coauthors)
        return f"[Arxiv] {self.titre} - co-auteurs : {liste}"

    