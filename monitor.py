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
    
    # Busca todas as tags <small> e elementos com classe 'small'
    elementos_small = soup.find_all(lambda tag: tag.name == "small" or "small" in tag.get("class", []))
    
    datas = []

    for el in elementos_small:
        texto = el.get_text(strip=True)
        try:
            data_str = texto.split()[0]  # Pega apenas a parte da data: dd/mm/yyyy
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
            texto_completo = el.find_parent().get_text(strip=True)
            datas.append((data, texto_completo))
        except (ValueError, IndexError):
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
