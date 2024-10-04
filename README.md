Développement et déploiement d'un agent LLM sur Azure

- Récupérer les données
- Construire un agent basé sur un LLM, capable de répondre à plusieurs prompts tels que des questions concernant des documents textes, ou une base de données.
- Construire une API pour servir ce modèle.
- (Facultatif) Déployer cette application sur le Cloud pour la rendre disponible.

Contexte du projet

    Créer un dataset à partir de https://gutenberg.org/ :
    * votre dataset doit contenir au moins 5000 livres
    * indications : scrapper la partie "about" de chaque livre

    Créer un agent langchain capable de :
    * répondre à des questions sur les livres et leurs attributs (exemple : de quels sujets traite tel ou tel livre ?)
    * récupérer une liste des noms des personnages mentionnés dans le résumé du livre
    * si demandé par l'utilisateur, récupérer tout le texte d'un livre (.txt dispo sur https://gutenberg.org/) et répondre à des questions dessus

    Évaluer l'agent sur les parties utilisant du RAG

    Rendre l'agent requêtable par API avec FastAPI

    (Facultatif) Déployer l'API sur Azure