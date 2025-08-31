# src/utils/llm.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()



def get_llm():
    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "openai":
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    else:
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

