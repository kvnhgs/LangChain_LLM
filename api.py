from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import pandas as pd
import spacy
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.schema import Document
from rich import print
from rich.console import Console
from rich.table import Table

load_dotenv()

app = FastAPI()

console = Console()

azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

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

print("Modèle d'embedding configuré")

df_books = pd.read_csv('Files/gutenberg_ebooks.csv')
print("Données des livres chargées")

df_books['Summary'] = df_books['Summary'].fillna('').astype(str)
print("Nettoyage des données effectué")

# Limiter le nombre de livres pour tester
df_books = df_books.head(100)

# Charger les résumés de livres
book_summaries = df_books['Summary'].tolist()
print(f"Nombre de résumés chargés: {len(book_summaries)}")

# Créer un index vectoriel à partir des documents et embeddings
def create_vector_index(texts, embedding_model):
    print("Création des embeddings")
    docs = [Document(page_content=text) for text in texts]
    embeddings = [embedding_model.embed_query(text) for text in texts]
    print("Embeddings générés")
    
    # Créer un index vectoriel à partir des documents et des embeddings générés
    vector_store = DocArrayInMemorySearch.from_documents(docs, embedding_model)
    print("Index vectoriel créé")
    
    return vector_store

# Créer l'index vectoriel
index = create_vector_index(book_summaries, embedding_model)

# Fonction pour répondre à des questions sur les attributs des livres
def get_book_info(book_title):
    book_info = df_books[df_books['Title'].str.contains(book_title, case=False, na=False)]
    if not book_info.empty:
        return book_info.iloc[0].to_dict()
    else:
        return None

# Fonction pour envoyer une question à l'API Azure OpenAI
def ask_llm(question):
    prompt_template = PromptTemplate(
        template="You are a helpful assistant. {question}",
        input_variables=["question"]
    )
    formatted_prompt = prompt_template.format(question=question)
    response = llm.invoke(formatted_prompt)
    return response

# Fonction pour rechercher les documents pertinents et poser une question à Azure OpenAI
def retrieve_and_answer(question):
    print(f"Recherche pour la question: {question}")
    
    # Rechercher dans l'index les documents pertinents
    relevant_docs = index.similarity_search(question)
    
    print(f"{len(relevant_docs)} documents pertinents trouvés")

    # Si des documents sont trouvés, les inclure dans la question
    if relevant_docs:
        combined_prompt = f"Here are some relevant documents:\n\n"
        for doc in relevant_docs:
            combined_prompt += f"{doc.page_content}\n"
        combined_prompt += f"\nNow, answer the following question based on these documents: {question}"
    else:
        combined_prompt = f"No relevant documents found. Please answer the following question: {question}"
    
    # Poser la question à Azure OpenAI
    response = ask_llm(combined_prompt)
    return response

# Modèles pour les requêtes API
class BookQuery(BaseModel):
    title: str

class QuestionQuery(BaseModel):
    question: str

# Endpoint pour obtenir des informations sur un livre
@app.post("/book_info/")
def get_book_info_api(query: BookQuery):
    book_info = get_book_info(query.title)
    if book_info:
        return book_info
    else:
        raise HTTPException(status_code=404, detail="Book not found.")

# Endpoint pour poser une question et obtenir une réponse à partir des documents et du LLM
@app.post("/ask_question/")
def ask_question_api(query: QuestionQuery):
    response = retrieve_and_answer(query.question)
    return {"response": response}
