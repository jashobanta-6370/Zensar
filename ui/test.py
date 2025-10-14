import requests

try:
    r = requests.get("http://127.0.0.1:11434/v1/models")
    if r.status_code == 200:
        print("✅ Ollama server is reachable!")
        print("Models available:", r.json())
    else:
        print(f"⚠️ Received status code: {r.status_code}")
except Exception as e:
    print(f"❌ Error connecting to Ollama: {e}")
