import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://www.cariacica.es.gov.br/documento/ver/36/detalhes"
ARQUIVO_DATA = "data_pmc.txt"
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

def get_data_publicacao():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Procura o elemento que contém "Data de publicação"
    label = soup.find(string=lambda t: "Data de publicação" in t)
    if not label:
        print("Campo 'Data de publicação' não encontrado.")
        return None

    # O valor costuma estar no elemento <td> seguinte ou em um <strong>
    td = label.find_parent("td") if hasattr(label, "find_parent") else None
    if td:
        proximo_td = td.find_next_sibling("td")
        if proximo_td:
            data_texto = proximo_td.get_text(strip=True)
        else:
            data_texto = td.get_text(strip=True)
    else:
        data_texto = label.strip()

    # Ajusta formato para converter corretamente
    try:
        data_publicacao = datetime.strptime(data_texto, "%d/%m/%Y").date()
        print(f"Data de publicação encontrada: {data_publicacao}")
        return data_publicacao
    except ValueError:
        print(f"Formato de data inválido: {data_texto}")
        return None

def main():
    data_site = get_data_publicacao()
    if data_site is None:
        print("Nenhuma data encontrada no site.")
        return

    ultima_data = ler_ultima_data()

    if data_site > ultima_data:
        mensagem = (f"📢 Nova publicação no site da Prefeitura de Cariacica:\n"
                    f"<b>{data_site.strftime('%d/%m/%Y')}</b>\n"
                    f"Acesse: {URL}")
        sucesso = enviar_telegram(mensagem)
        if sucesso:
            print("Mensagem enviada com sucesso.")
            salvar_data(data_site)
        else:
            print("Erro ao enviar mensagem no Telegram.")
    else:
        print("Nenhuma nova publicação encontrada.")

if __name__ == "__main__":
    main()
