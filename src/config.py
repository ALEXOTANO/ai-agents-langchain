"""
LLM Configuration - Plug & Play between OpenAI and Ollama
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

load_dotenv()


def get_llm():
    """
    Factory function to get the appropriate LLM based on configuration.
    
    Args:
        use_local: If True, use Ollama locally. If False, use OpenAI.
                   If None, read from USE_LOCAL_LLM environment variable.
    
    Returns:
        ChatOpenAI or ChatOllama instance
    """
    use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    
    if use_local:
        return ChatOllama(model="ministral-3:3b", temperature=0)
    else:
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)



