import requests
from bs4 import BeautifulSoup
import os

URL = "https://selecao.es.gov.br/PaginaConcurso/Index/659"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def get_ultima_publicacao():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select(".card.mb-3")
    if not cards:
        return None
    return cards[0].text.strip()

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    requests.post(url, data=data)

def ler_estado():
    try:
        with open("ultima_publicacao.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def salvar_estado(pub):
    with open("ultima_publicacao.txt", "w") as f:
        f.write(pub)

def verificar():
    ultima = get_ultima_publicacao()
    if not ultima:
        return
    anterior = ler_estado()
    if ultima != anterior:
        salvar_estado(ultima)
        enviar_telegram(f"📢 Nova publicação detectada!\n\n{ultima}\n\n{URL}")

if __name__ == "__main__":
    verificar()
