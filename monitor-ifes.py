import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://www.ifes.edu.br/processosseletivos/servidores/item/3127-concurso-publico-01-2024-docentes"
ARQUIVO_DATA = "ultima_data_ifes.txt"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def ler_ultima_data():
    try:
        with open(ARQUIVO_DATA, "r") as f:
            data_str = f.read().strip()
            return datetime.strptime(data_str, "%d/%m/%Y").date()
    except (FileNotFoundError, ValueError):
        return datetime.min.date()

def salvar_data(data):
    with open(ARQUIVO_DATA, "w") as f:
        f.write(data.strftime("%d/%m/%Y"))

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, data=data)
    return resp.ok

def get_maior_data():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    datas = []
    for a in soup.find_all("a"):
        texto = a.get_text(strip=True)
        try:
            partes = texto.split()
            for parte in partes:
                if len(parte) == 10 and parte[2] == '/' and parte[5] == '/':
                    data = datetime.strptime(parte, "%d/%m/%Y").date()
                    datas.append((data, texto))
                    break
        except:
            continue

    if not datas:
        return None, None

    return max(datas, key=lambda x: x[0])

def main():
    maior_data, texto = get_maior_data()
    if maior_data is None:
        print("Nenhuma data encontrada no site.")
        return

    ultima_data = ler_ultima_data()

    if maior_data > ultima_data:
        mensagem = (f"🚨 Nova data detectada no IFES:\n<b>{maior_data.strftime('%d/%m/%Y')}</b>\n"
                    f"Descrição: {texto}\n"
                    f"Acesse: {URL}")
        sucesso = enviar_telegram(mensagem)
        if sucesso:
            print("Mensagem enviada com sucesso.")
            salvar_data(maior_data)
        else:
            print("Erro ao enviar mensagem no Telegram.")
    else:
        print("Nenhuma data nova.")

if __name__ == "__main__":
    main()
