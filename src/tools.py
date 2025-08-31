
from .embeddings import build_policies_store




def policy_lookup(data:dict) -> str:
    POLICYS_STORE = build_policies_store()
    
    category = data.get("category", "General")
    subject = data.get("subject", "")
    description = data.get("description", "")

    query = f"Category: {category}, Subject: {subject}, Description: {description}"
    docs = POLICYS_STORE.similarity_search(query, k=2)
    return "\n".join([d.page_content for d in docs])