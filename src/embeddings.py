# src/utils/embeddings.py
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()


def load_or_build_store(category, filepath, embeddings):
    """
    Load FAISS store from disk if it exists.
    If not, build from the KB text file and save it.
    """
    store_path = f"src/stores/{category.lower()}_store"

    # Load from disk if exists
    if os.path.exists(store_path):
        return FAISS.load_local(store_path, embeddings, allow_dangerous_deserialization=True)

    # Otherwise, build from text file
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([text])

    store = FAISS.from_documents(docs, embeddings)
    store.save_local(store_path)  # save for future runs

    return store


def build_vectorstores():
    """
    Build or load all vectorstores (Billing, Technical, Security, General).
    Returns a dict: {category: FAISS store}
    """
    #embeddings = GoogleGenerativeAIEmbeddings( model="models/embedding-001",  google_api_key=os.getenv("GOOGLE_API_KEY") )
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    kb_files = {
        "Billing":  "src/data/billing.txt",
        "Technical": "src/data/technical.txt",
        "Security": "src/data/security.txt",
        "General": "src/data/general.txt",
    }

    stores = {}
    for category, filepath in kb_files.items():
        stores[category] = load_or_build_store(category, filepath, embeddings)

    return stores

def build_policies_store():
    #embeddings = GoogleGenerativeAIEmbeddings(    model="models/embedding-001",    google_api_key=os.getenv("GOOGLE_API_KEY") )
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    filepath = "src/data/policies.txt"
    store = load_or_build_store("Policies", filepath, embeddings)
    return store