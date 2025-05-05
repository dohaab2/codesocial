import os
import requests
import time
from dotenv import load_dotenv

# Charger la clé API
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Liste des Google Docs à traiter
google_docs = [
    "https://docs.google.com/document/d/1R1_KTzjnx0md65rL8Im3g-Aa5mLKNnVm/export?format=txt",
    "https://docs.google.com/document/d/1DgHLS-qHOVRhvSr2ZffZimH-Ltes8tAl/export?format=txt",
    "https://docs.google.com/document/d/13LTp5DcWa78qms8E6EFHFIW-8_2xNWNT/export?format=txt",
    "https://docs.google.com/document/d/1gR8q3TIZ5sgcJSeNxovVvGW622CxHsKv/export?format=txt",
    "https://docs.google.com/document/d/1Cp2GYDIsm0iTqcmNW-GPQvTKMbD5s_7F/export?format=txt",
    "https://docs.google.com/document/d/1roUeJdhiUWvQZqoBBEOSQaXX6J_wujqL/export?format=txt",
    "https://docs.google.com/document/d/1hVu4WC2fIaBCCYWVQ29MySr-DNwl495-/export?format=txt",
    "https://docs.google.com/document/d/1MpSydy3-JkaozqfJywWW-t93KRVqQATw/export?format=txt",
    "https://docs.google.com/document/d/1IR7cTAK37J5qO-t1lqouXD--lW65krBI/export?format=txt",
    "https://docs.google.com/document/d/1snOlmewj18oFhNDixWbgLN5uly_GoRpB/export?format=txt"
]

# Estimation des tokens
def estimate_tokens(text):
    return int(len(text) / 3.5)

# Découpage intelligent
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

# Paramètres Groq API
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Résultat global
global_result = ""

# Parcourir chaque document
for idx_doc, doc_url in enumerate(google_docs):
    print(f"\n📄 Traitement du document {idx_doc + 1}/{len(google_docs)}")

    response_doc = requests.get(doc_url)
    if response_doc.status_code == 200:
        full_text = response_doc.text
    else:
        print("  ❌ Erreur de téléchargement")
        continue

    chunks = split_text_smart(full_text, max_tokens=5000)
    result = f"\n=============================\nRésultats pour le document {idx_doc + 1}\n=============================\n"

    for idx, chunk in enumerate(chunks):
        print(f"  → Envoi du morceau {idx + 1}/{len(chunks)}...")

        prompt = f"""Voici une partie d'un document :

{chunk}

Peux-tu analyser cette partie du texte et identifier les principaux thèmes sociologiques abordés ?
Pour chaque thème identifié, indique :

1. Le nom du thème
2. Une courte explication (1-2 phrases)
3. Un ou deux verbatim (extraits littéraux du texte) qui illustrent ce thème

Merci de structurer ta réponse de manière claire et lisible.
"""

        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        success = False
        while not success:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                result += f"\n--- Thématiques du morceau {idx + 1} ---\n{content}\n"
                success = True
            elif response.status_code == 429:
                print("    Rate limit atteint, pause de 5s...")
                time.sleep(5)
            else:
                print(f"    Erreur : {response.status_code}")
                print(response.text)
                success = True
        time.sleep(2)

    # Ajouter le résultat du doc au résultat global
    global_result += result

# Sauvegarde unique dans un seul fichier
with open("result_llm2.txt", "w", encoding="utf-8") as out:
    out.write(global_result)

print("✅ Tous les résultats ont été enregistrés dans result_llm2.txt")
