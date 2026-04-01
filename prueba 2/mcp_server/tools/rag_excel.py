import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "..", "index", "faiss_index")

print(f"Cargando índice FAISS desde: {INDEX_PATH}")

embeddings = OllamaEmbeddings(model="nomic-embed-text")

vectorstore = FAISS.load_local(
    INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

def excel_rag_search(query: str) -> str:
    results = vectorstore.similarity_search(query, k=4)
    return "\n\n".join([doc.page_content for doc in results])