import os
import requests
import time
from dotenv import load_dotenv

# Charger la clé API
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Télécharger le texte du Google Doc
doc_url = "https://docs.google.com/document/d/1R1_KTzjnx0md65rL8Im3g-Aa5mLKNnVm/edit"
response_doc = requests.get(doc_url)

if response_doc.status_code == 200:
    full_text = response_doc.text
else:
    print("Erreur pour récupérer le Google Doc")
    full_text = ""

# Fonction pour estimer les tokens (environ 3.5 caractères/token en français)
def estimate_tokens(text):
    return int(len(text) / 3.5)

# Fonction pour découper en respectant la limite de tokens
def split_text_smart(text, max_tokens=5000):
    parts = []
    while estimate_tokens(text) > max_tokens:
        cut_point = int(max_tokens * 3.5)
        split_index = text[:cut_point].rfind('.')
        if split_index == -1:
            split_index = cut_point
        parts.append(text[:split_index + 1].strip())
        text = text[split_index + 1:]
    if text.strip():
        parts.append(text.strip())
    return parts

# Découper le texte
chunks = split_text_smart(full_text, max_tokens=5000)

# Définir l'URL de l'API
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer " + api_key,
    "Content-Type": "application/json"
}

# Résultat global
full_summary = ""

# Parcourir les morceaux
for idx, chunk in enumerate(chunks):
    print(f"\nEnvoi du morceau {idx + 1}/{len(chunks)}...")

    prompt_text = f"""Voici une partie d'un document :

{chunk}

Peux-tu analyser cette partie du texte et identifier les principaux thèmes sociologiques abordés ?
Merci de répondre sous forme d'une liste claire.
"""

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt_text}
        ]
    }

    success = False
    while not success:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            partial_summary = response.json()['choices'][0]['message']['content']
            full_summary += f"\n--- Thématiques du morceau {idx + 1} ---\n{partial_summary}\n"
            success = True
        elif response.status_code == 429:
            print("Rate limit atteint. Pause de 5 secondes...")
            time.sleep(5)
        else:
            print(f"Erreur pour le morceau {idx + 1} : {response.status_code}")
            print(response.text)
            success = True  # Ne pas bloquer le script même en cas d'erreur

    time.sleep(2)  # Pause légère pour éviter le rate limit

# Affichage final
print("\nThématiques sociologiques extraites :\n")
print(full_summary)

# Sauvegarde dans un fichier texte
with open("result.txt", "w", encoding="utf-8") as f:
    f.write(full_summary)
