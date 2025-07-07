import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os

URL = "https://www.tjes.jus.br/portal-transparencia/pessoal/contratacao-temporaria/"
ARQUIVO_DATA = "ultima_data_tjes.txt"
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

def get_data_atualizacao():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    for td in soup.find_all("td"):
        texto = td.get_text(strip=True)
        if "última atualização" in texto.lower():
            match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
            if match:
                data = datetime.strptime(match.group(1), "%d/%m/%Y").date()
                print(f"Data encontrada: {data} - texto: {texto}")
                return data, texto
    return None, None

def main():
    maior_data, texto = get_data_atualizacao()
    if maior_data is None:
        print("Nenhuma data encontrada no site.")
        return

    ultima_data = ler_ultima_data()

    if ultima_data > maior_data:
        print("Data no arquivo é mais recente que a do site. Ignorando.")
        return

    if maior_data > ultima_data:
        mensagem = (f"📢 Atualização no site do TJES:\n<b>{maior_data.strftime('%d/%m/%Y')}</b>\n"
                    f"Acesse: {URL}")
        sucesso = enviar_telegram(mensagem)
        if sucesso:
            print("Mensagem enviada com sucesso.")
            salvar_data(maior_data)
        else:
            print("Erro ao enviar mensagem no Telegram.")
    else:
        print("Nenhuma atualização nova.")

if __name__ == "__main__":
    main()
