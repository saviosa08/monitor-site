import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://selecao.es.gov.br/PaginaConcurso/Index/659"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ARQUIVO_DATA = "ultima_data.txt"

def get_maior_data():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    elementos_small = soup.find_all(lambda tag: tag.name == "small" or "small" in tag.get("class", []))
    datas = []

    for el in elementos_small:
        texto = el.get_text(strip=True)
        try:
            data_str = texto.split()[0]  # Pega só o dd/mm/yyyy
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
            texto_completo = el.find_parent().get_text(strip=True)
            datas.append((data, texto_completo))
        except (ValueError, IndexError):
            continue

    if not datas:
        return None, None

    return max(datas, key=lambda x: x[0])

def ler_ultima_data_salva():
    if not os.path.exists(ARQUIVO_DATA):
        return datetime.min.date()  # data muito antiga
    with open(ARQUIVO_DATA, "r") as f:
        try:
            return datetime.strptime(f.read().strip(), "%d/%m/%Y").date()
        except ValueError:
            return datetime.min.date()

def salvar_data(data):
    with open(ARQUIVO_DATA, "w") as f:
        f.write(data.strftime("%d/%m/%Y"))

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def verificar():
    data_site, texto = get_maior_data()
    if not data_site:
        print("Nenhuma data encontrada.")
        return

    data_salva = ler_ultima_data_salva()
    if data_site > data_salva:
        mensagem = f"📢 Nova publicação encontrada em <b>{data_site.strftime('%d/%m/%Y')}</b>📅\n\n🔗 {URL}"
        enviar_telegram(mensagem)
        salvar_data(data_site)
        print("Mensagem enviada.")

if __name__ == "__main__":
    verificar()
