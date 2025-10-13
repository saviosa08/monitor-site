import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

# Configurações
URL = "https://www.cariacica.es.gov.br/documento/ver/36/detalhes"
ARQUIVO_DATA = "data_pmc.txt"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ENVIAR_TELEGRAM = True if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID else False

# Cabeçalhos para evitar bloqueio 403
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

def ler_ultima_data():
    try:
        with open(ARQUIVO_DATA, "r", encoding="utf-8") as f:
            data_str = f.read().strip()
            return datetime.strptime(data_str, "%d/%m/%Y").date()
    except (FileNotFoundError, ValueError):
        return datetime.min.date()

def enviar_telegram(mensagem):
    if not ENVIAR_TELEGRAM:
        print("ENVIAR_TELEGRAM desativado ou sem credenciais. Não enviando mensagem.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        return resp.ok
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")
        return False

def get_datas_da_pagina():
    """Busca todas as datas em <td> no formato dd/mm/yyyy."""
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
    except Exception as e:
        print(f"Erro ao acessar {URL}: {e}")
        return []

    if resp.status_code != 200:
        print(f"Resposta HTTP {resp.status_code} ao acessar {URL}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    padrao_data = re.compile(r"^\s*(\d{2}/\d{2}/\d{4})\s*$")
    datas_encontradas = []

    for td in soup.find_all("td"):
        texto = td.get_text(strip=True)
        if padrao_data.match(texto):
            try:
                data_obj = datetime.strptime(texto, "%d/%m/%Y").date()
                datas_encontradas.append(data_obj)
            except ValueError:
                continue

    return datas_encontradas

def main():
    datas = get_datas_da_pagina()

    if not datas:
        print("Nenhuma data no formato dd/mm/yyyy encontrada nos <td> da página.")
        return

    print("Datas encontradas:")
    for d in sorted(datas):
        print(" -", d.strftime("%d/%m/%Y"))

    maior_data_site = max(datas)
    ultima_data = ler_ultima_data()

    print(f"\nMaior data no site: {maior_data_site.strftime('%d/%m/%Y')}")
    print(f"Data no arquivo:    {ultima_data.strftime('%d/%m/%Y')}")

    if maior_data_site > ultima_data:
        print(">>> Há uma data mais recente no site.")
        mensagem = (
            f"📢 Nova publicação detectada na Prefeitura de Cariacica!\n"
            f"<b>{maior_data_site.strftime('%d/%m/%Y')}</b>\n"
            f"Acesse: {URL}"
        )
        if ENVIAR_TELEGRAM:
            enviado = enviar_telegram(mensagem)
            print("Mensagem enviada via Telegram." if enviado else "Falha ao enviar mensagem.")
    else:
        print("Nenhuma nova data detectada.")

if __name__ == "__main__":
    main()
