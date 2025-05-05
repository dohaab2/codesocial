import os
import requests
from dotenv import load_dotenv

# Charger la clé API
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Lire et tronquer les fichiers à 10 000 caractères (≈ 2800 tokens chacun)
def read_and_truncate(filepath, max_chars=10000):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return text[:max_chars]

text1 = read_and_truncate("result_llm1.txt")
text2 = read_and_truncate("result_llm2.txt")

# Préparer le prompt
prompt = f"""
Voici deux analyses produites par des modèles LLM sur différents documents ou parties de documents.

Analyse 1 :
{text1}

Analyse 2 :
{text2}

Peux-tu me faire une synthèse ou un compte rendu global de ce que ces deux analyses permettent de comprendre ?
Tu peux dégager les points communs, les différences, les grands thèmes sociologiques récurrents, les nuances.
"""

# Envoi à l'API Groq
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "llama3-8b-8192",  # ou "llama3-70b-8192", si ton quota le permet
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

response = requests.post(url, headers=headers, json=payload)

# Traitement de la réponse
if response.status_code == 200:
    summary = response.json()['choices'][0]['message']['content']
    print("\n📝 Synthèse générée :\n")
    print(summary)

    # Sauvegarder
    with open("synthese.txt", "w", encoding="utf-8") as out:
        out.write(summary)
    print("\n✅ Synthèse enregistrée dans synthese.txt")
else:
    print(f"❌ Erreur : {response.status_code}")
    print(response.text)
