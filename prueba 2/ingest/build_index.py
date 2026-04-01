import os
import pandas as pd
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(BASE_DIR, "data", "data.xlsx")
INDEX_PATH = os.path.join(BASE_DIR, "index", "faiss_index")

def load_excel():
    print(f"📄 Leyendo Excel desde: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH)

    docs = []
    for _, row in df.iterrows():
        text = " ".join([str(v) for v in row.values if pd.notna(v)])
        docs.append(text)

    return docs

def build_index():
    docs = load_excel()

    print("✂️ Dividiendo en chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.create_documents(docs)

    print("Generando embeddings con Ollama...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    print("Creando índice FAISS...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(INDEX_PATH, exist_ok=True)
    vectorstore.save_local(INDEX_PATH)

    print("Índice FAISS generado correctamente.")

if __name__ == "__main__":
    build_index()