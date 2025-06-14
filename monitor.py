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
    painels = soup.select(".panel.panel-default")
    datas = []

    for painel in painels:
        cabecalho = painel.select_one(".panel-heading")
        if not cabecalho:
            continue

        small = cabecalho.find("small")
        if not small:
            small = cabecalho.find(class_="small")
        if not small:
            continue

        texto_data = small.text.strip().split()[0]  # ex: "07/04/2025"
        try:
            data = datetime.strptime(texto_data, "%d/%m/%Y").date()
            texto = cabecalho.text.strip()
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
