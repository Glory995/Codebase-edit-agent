"""
client.py

Low-level HTTP client for the Ollama API.
Wraps the /api/generate endpoint behind a clean function.
Swapping to a different provider later means changing this file only.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
DEFAULT_MODEL = "llama3.2"


def complete(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send a prompt to the local Ollama model and return the response text.

    Args:
        prompt: The full prompt string to send.
        model:  The Ollama model name to use.

    Returns:
        The model's response as a plain string.

    Raises:
        requests.HTTPError: If the Ollama API returns a non-2xx status.
        requests.ConnectionError: If Ollama is not running.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()

    return response.json()["response"]


if __name__ == "__main__":
    # Quick smoke test — run directly with: python client.py    
    answer = complete("In one sentence, Do you know Glory Ojoma Simon?")
    print(answer)
