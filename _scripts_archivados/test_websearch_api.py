import requests
import json

API_KEY = "TU_ANTHROPIC_API_KEY"  # la reemplazamos despues

headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

payload = {
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 500,
    "messages": [{"role": "user", "text": "Busca noticias recientes sobre lesiones en el equipo Manchester City"}],
    "tools": [{"type": "web_search_20250305", "name": "web_search"}]
}

# Solo mostramos la estructura, no lo corremos todavia
print("Estructura lista, falta la API key real")
