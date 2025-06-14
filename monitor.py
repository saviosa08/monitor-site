import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://selecao.es.gov.br/PaginaConcurso/Index/659"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def get_maior_data():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select(".card.mb-3")
    datas = []

    for card in cards:
        texto = card.text.strip()
        if "-" in texto:
            parte_data = texto.split("-")[0].strip()
            try:
                data = datetime.strptime(parte_data, "%d/%m/%Y").date()
                datas.append((data, texto))
            except ValueError:
                continue

    if not datas:
        return None, None

    return max(datas, key=lambda x: x[0])

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def verificar():
    data, texto = get_maior_data()
    if data:
        mensagem = f"📅 Maior data encontrada: <b>{data.strftime('%d/%m/%Y')}</b>\n📝 {texto}\n\n🔗 {URL}"
    else:
        mensagem = f"⚠️ Nenhuma data encontrada na página.\n\n🔗 {URL}"

    enviar_telegram(mensagem)

if __name__ == "__main__":
    verificar()
