import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

URL = "https://portal.ifsuldeminas.edu.br/index.php/pos-graduacao-ead2/pos-graduacao-abertos-ead/6988-edital-154-2024-cursos-de-pos-graduacao-lato-sensu-especializacao-ead-2-semestre-de-2025"
ARQUIVO_DATA = "data_pos.txt"
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
    if not resp.ok:
        print("Erro ao enviar mensagem:", resp.text)
    return resp.ok

def get_maior_data():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    datas = []
    pattern = r"\b\d{2}/\d{2}/\d{4}\b"  # Formato dd/mm/yyyy

    for td in soup.find_all("td"):
        texto = td.get_text(" ", strip=True)
        matches = re.findall(pattern, texto)
        for data_str in matches:
            try:
                data = datetime.strptime(data_str, "%d/%m/%Y").date()
                print(f"Data encontrada: {data} - texto: {texto}")
                datas.append((data, texto))
            except ValueError:
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
    print(f"Última data salva: {ultima_data}")
    print(f"Maior data encontrada: {maior_data}")

    if maior_data > ultima_data:
        mensagem = (f"🚨 Nova data detectada no IFSULDEMINAS:\n<b>{maior_data.strftime('%d/%m/%Y')}</b>\n"
                
                    f"Acesse: {URL}")
        if enviar_telegram(mensagem):
            print("Mensagem enviada com sucesso.")
            salvar_data(maior_data)
        else:
            print("Erro ao enviar mensagem.")
    else:
        print("Nenhuma data nova.")

if __name__ == "__main__":
    main()
