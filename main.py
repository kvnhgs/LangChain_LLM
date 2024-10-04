import os
import requests
import pandas as pd
import spacy
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_openai import AzureOpenAIEmbeddings  # Mise à jour ici
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.document_loaders import TextLoader  # Mise à jour ici
from rich import print  # Import pour afficher les résultats formatés
from rich.console import Console  # Utilisé pour afficher les tables ou sections formatées
from rich.table import Table

# Initialiser la console Rich
console = Console()

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les informations d'API Azure OpenAI depuis les variables d'environnement
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Configuration du modèle Azure OpenAI (AzureChatOpenAI)
llm = AzureChatOpenAI(
    azure_endpoint=azure_openai_endpoint,
    azure_deployment=azure_openai_deployment_name,
    openai_api_version=azure_openai_api_version
)

# Embedding model for vector store
embedding_model = AzureOpenAIEmbeddings(
    openai_api_key=azure_openai_api_key,
    azure_deployment='text-embedding-3-large',
    azure_endpoint=azure_openai_endpoint,
    openai_api_version="2023-05-15",
    chunk_size=500
)

# Charger les données des livres (par exemple, un CSV avec 20 000 lignes)
df_books = pd.read_csv('Files/gutenberg_ebooks.csv')

# Initialiser spaCy pour l'extraction des personnages
nlp = spacy.load("en_core_web_sm")

# Fonction pour répondre à des questions sur les attributs des livres
def get_book_info(book_title):
    book_info = df_books[df_books['Title'].str.contains(book_title, case=False, na=False)]
    if not book_info.empty:
        return book_info.iloc[0].to_dict()  # Retourner les attributs du premier livre correspondant
    else:
        return "Book not found."

# Fonction pour extraire les personnages mentionnés dans le résumé d'un livre
def extract_characters_from_summary(summary):
    doc = nlp(summary)
    characters = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    return characters if characters else "No characters found."

# Fonction pour récupérer le texte complet d'un livre à partir de Project Gutenberg
def fetch_full_text(book_id):
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"  # Modification ici : vérifie le format d'URL correct
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Unable to retrieve the full text of this book."

# Fonction pour poser des questions générales à Azure OpenAI
def ask_llm(question):
    prompt_template = PromptTemplate(
        template="You are a helpful assistant. {question}",
        input_variables=["question"]
    )
    formatted_prompt = prompt_template.format(question=question)
    response = llm.invoke(formatted_prompt)  # Utiliser la méthode invoke pour appeler l'API
    return response

# Chargement du contenu texte pour l'indexation
loader = TextLoader('loader.txt')  # Remplace par le chemin réel du fichier

# Création de l'index avec AzureOpenAIEmbeddings
index = VectorstoreIndexCreator(
    embedding=embedding_model,
    vectorstore_cls=DocArrayInMemorySearch
).from_loaders([loader])

# Exemple d'utilisation : répondre à des questions sur un livre
book_title = "Tarzan of the Apes"
book_info = get_book_info(book_title)

# Afficher les informations du livre avec une table formatée
table = Table(title="Book Information", show_header=True, header_style="bold magenta")
table.add_column("Key", justify="right")
table.add_column("Value", justify="left")

for key, value in book_info.items():
    table.add_row(key, str(value))

console.print(table)

# Exemple d'interaction avec le LLM
question = "Give me all the book about Keanu Reeves'?"
llm_response = ask_llm(question)

# Afficher la réponse de l'LLM formatée
console.print("\n[b]Response from LLM:[/b]", llm_response)
