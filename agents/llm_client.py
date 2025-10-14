import subprocess
import json
import requests
from typing import Optional

# Ollama HTTP API (if enabled)
OLLAMA_HTTP_URL = "http://localhost:11434/v1/completions"
# Ollama CLI path
OLLAMA_CLI = "ollama"

# Default model name from your local installation
DEFAULT_MODEL = "llama3:8b"


def query_ollama_http(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 200) -> Optional[str]:
    try:
        payload = {"model": model, "prompt": prompt, "max_tokens": max_tokens}
        r = requests.post(OLLAMA_HTTP_URL, json=payload, timeout=30)  # increased timeout
        if r.status_code == 200:
            data = r.json()
            # Check multiple possible return formats
            if "completion" in data:
                return data["completion"]
            elif "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0].get("text")
            elif "text" in data:
                return data["text"]
            else:
                return json.dumps(data)
    except Exception as e:
        print("Ollama HTTP error:", e)
        return None


def query_ollama_cli(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 20) -> Optional[str]:
    try:
        proc = subprocess.run(
            [OLLAMA_CLI, "run", model, "--no-stream"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        if proc.returncode == 0:
            out = proc.stdout.strip()
            return out if out else None
    except Exception as e:
        print("Ollama CLI error:", e)
        return None
    return None


def query_llm(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Query Ollama Llama3 model either via HTTP API or CLI.
    Returns a fallback message if the model is not reachable.
    """
    # First try HTTP API
    http_ans = query_ollama_http(prompt, model=model)
    if http_ans:
        return http_ans

    # Then try CLI
    cli_ans = query_ollama_cli(prompt, model=model)
    if cli_ans:
        return cli_ans

    # Fallback notice
    return (
        f"⚠️ Ollama model '{model}' not reachable.\n"
        "Start Ollama server in a terminal with:\n"
        "   ollama pull llama3 && ollama serve\n\n"
        "Fallback analysis:\n"
        "- Review short & long MA trends from rules.\n"
        "- Check ViT trend if chart uploaded.\n"
        "- Always verify with real-time market data."
    )
