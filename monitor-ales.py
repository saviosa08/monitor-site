import requests
from bs4 import BeautifulSoup
import os
import re

URL = "https://novo.ibgpconcursos.com.br/inscricoes_abertas.jsp"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    resp = requests.post(url, data=data)
    if not resp.ok:
        print("Erro no envio para o Telegram:", resp.text)
    return resp.ok

def verificar_assembleia():
    try:
        resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except Exception as e:
        print("Erro ao acessar o site:", e)
        return False, None

    soup = BeautifulSoup(resp.text, "html.parser")

    padrao = re.compile(r"\b(MG)\b", re.IGNORECASE)
    encontrados = []

    for h2 in soup.find_all("h2"):
        texto = h2.get_text(strip=True)
        if padrao.search(texto):
            encontrados.append(texto)

    if encontrados:
        return True, list(dict.fromkeys(encontrados))  # remove duplicatas
    else:
        return False, None

def main():
    aberto, titulos = verificar_assembleia()
    if aberto:
        linhas = "\n".join(f"- {t}" for t in titulos)
        mensagem = (
            "🚨 Inscrições abertas detectadas para *Assembleia Legislativa ES*:\n\n"
            f"🔎 Acesse: {URL}"
        )
        if enviar_telegram(mensagem):
            print("Mensagem enviada com sucesso.")
        else:
            print("Erro ao enviar mensagem.")
    else:
        print("Nenhuma inscrição da AL ES encontrada.")

if __name__ == "__main__":
    main()
