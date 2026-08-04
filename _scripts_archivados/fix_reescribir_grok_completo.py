with open("analisis_ia_diario_completo.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }"""

new = """    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }"""

if old in content:
    content = content.replace(old, new, 1)
    print("OK: headers actualizados para Grok")
else:
    print("ERROR headers")

old2 = """    payload = {
        "model": "claude-sonnet-5",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3, "allowed_domains": ["espn.com", "fotmob.com", "sofascore.com", "fifa.com", "flashscore.com", "wikipedia.org", "365scores.com"]}]
    }

    try:
        resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=45)
        data = resp.json()
        texto_final = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                texto_final += block.get("text", "")"""

new2 = """    payload = {
        "model": "grok-4-fast",
        "input": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search"}]
    }

    try:
        resp = requests.post("https://api.x.ai/v1/responses", headers=headers, json=payload, timeout=45)
        data = resp.json()
        texto_final = ""
        for block in data.get("output", []):
            for c in block.get("content", []) or []:
                if c.get("type") == "output_text":
                    texto_final += c.get("text", "")"""

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("OK: payload y parseo actualizados para Grok")
else:
    print("ERROR payload")

with open("analisis_ia_diario_completo.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
