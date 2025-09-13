import os
from typing import Optional

def get_chat_model():
    """Get chat model based on LLM_PROVIDER environment variable"""
    provider = os.getenv("LLM_PROVIDER", "none").lower()

    if provider == "none":
        return None

    # For now, return None and use heuristics
    # TODO: Implement LangChain integration when dependencies are available
    return None

def get_embeddings_model():
    """Get embeddings model (optional for future use)"""
    # For now, return None
    # TODO: Implement when LangChain dependencies are available
    return None