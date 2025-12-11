from Document import Document, RedditDocument, ArxivDocument

# Factory pour créer des documents selon le type
class DocumentFactory:
    @staticmethod
    def create(source, titre, auteur, date, url, texte, extra=None):

        if source == "Reddit":
            return RedditDocument(titre, auteur, date, url, texte, extra)

        elif source == "Arxiv":
            return ArxivDocument(titre, auteur, date, url, texte, extra)

        else:
            return Document(titre, auteur, date, url, texte)
