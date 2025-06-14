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

def buscar_datas():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    datas = []

    # Extrai datas de todas as tags <a>
    for a in soup.find_all("a"):
        texto = a.get_text(strip=True)
        # Tenta extrair datas no formato dd/mm/yyyy
        try:
            # Pode ter outras coisas junto, tenta achar a parte de data com split e regex
            partes = texto.split()
            for parte in partes:
                if len(parte) == 10 and parte[2] == '/' and parte[5] == '/':
                    data = datetime.strptime(parte, "%d/%m/%Y").date()
                    datas.append(data)
        except:
            continue
    return datas

def main():
    datas_encontradas = buscar_datas()
    if not datas_encontradas:
        print("Nenhuma data encontrada no site.")
        return

    maior_data_site = max(datas_encontradas)
    ultima_data = ler_ultima_data()

    if maior_data_site > ultima_data:
        mensagem = (f"🚨 Nova data detectada no IFES:\n<b>{maior_data_site.strftime('%d/%m/%Y')}</b>\n"
                    f"Acesse: {URL}")
        sucesso = enviar_telegram(mensagem)
        if sucesso:
            print("Mensagem enviada com sucesso.")
            salvar_data(maior_data_site)
        else:
            print("Erro ao enviar mensagem no Telegram.")
    else:
        print("Nenhuma data nova.")

if __name__ == "__main__":
    main()
