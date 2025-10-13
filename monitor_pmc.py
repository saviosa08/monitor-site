import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

# Configurações
URL = "https://www.cariacica.es.gov.br/documento/ver/36/detalhes"
ARQUIVO_DATA = "data_pmc.txt"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def ler_ultima_data():
    """Lê a última data salva no arquivo local."""
    try:
        with open(ARQUIVO_DATA, "r") as f:
            data_str = f.read().strip()
            return datetime.strptime(data_str, "%d/%m/%Y").date()
    except (FileNotFoundError, ValueError):
        return datetime.min.date()

def salvar_data(data):
    """Grava a nova data no arquivo local."""
    with open(ARQUIVO_DATA, "w") as f:
        f.write(data.strftime("%d/%m/%Y"))

def enviar_telegram(mensagem):
    """Envia mensagem via bot do Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, data=data)
    return resp.ok

def get_maior_data():
    """Busca todas as datas no HTML e retorna a mais recente."""
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    padrao_data = re.compile(r"^\d{2}/\d{2}/\d{4}$")
    datas_encontradas = []

    for td in soup.find_all("td"):
        texto = td.get_text(strip=True)
        if padrao_data.match(texto):  # casa exatamente com o formato dd/mm/yyyy
            try:
                data = datetime.strptime(texto, "%d/%m/%Y").date()
                datas_encontradas.append(data)
                print(f"Data encontrada: {data}")
            except ValueError:
                continue

    if not datas_encontradas:
        return None

    return max(datas_encontradas)

def main():
    """Executa a verificação de nova publicação."""
    maior_data_site = get_maior_data()
    if not maior_data_site:
        print("Nenhuma data encontrada no site.")
        return

    ultima_data = ler_ultima_data()
    print(f"Última data registrada: {ultima_data}, maior data no site: {maior_data_site}")

    if maior_data_site > ultima_data:
        mensagem = (
            f"📢 Nova publicação no site da Prefeitura de Cariacica!\n"
            f"<b>Data de publicação:</b> {maior_data_site.strftime('%d/%m/%Y')}\n\n"
            f"Acesse: {URL}"
        )
        sucesso = enviar_telegram(mensagem)
        if sucesso:
            print("Mensagem enviada com sucesso.")
            salvar_data(maior_data_site)
        else:
            print("Erro ao enviar mensagem no Telegram.")
    else:
        print("Nenhuma nova publicação encontrada.")

if __name__ == "__main__":
    main()
