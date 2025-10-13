import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

# Configurações
URL = "https://www.cariacica.es.gov.br/documento/ver/36/detalhes"
ARQUIVO_DATA = "data_pmc.txt"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # pode ser None se não usar Telegram
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Toggle para enviar Telegram. Se não quiser notificações, deixe False.
ENVIAR_TELEGRAM = True if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID else False

def ler_ultima_data():
    """Lê a última data salva no arquivo local (formato dd/mm/YYYY)."""
    try:
        with open(ARQUIVO_DATA, "r", encoding="utf-8") as f:
            data_str = f.read().strip()
            if not data_str:
                print(f"Atenção: {ARQUIVO_DATA} está vazio. Usando data mínima.")
                return datetime.min.date()
            return datetime.strptime(data_str, "%d/%m/%Y").date()
    except FileNotFoundError:
        print(f"Atenção: arquivo {ARQUIVO_DATA} não encontrado. Usando data mínima.")
        return datetime.min.date()
    except ValueError:
        print(f"Atenção: formato inválido em {ARQUIVO_DATA}. Deve ser dd/mm/YYYY. Usando data mínima.")
        return datetime.min.date()

def enviar_telegram(mensagem):
    """Envia mensagem via bot do Telegram. Retorna True se OK."""
    if not ENVIAR_TELEGRAM:
        print("ENVIAR_TELEGRAM desativado ou credenciais ausentes. Não enviando mensagem.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.ok:
            return True
        else:
            print(f"Erro Telegram: status {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"Exceção ao enviar Telegram: {e}")
        return False

def get_datas_da_pagina():
    """Busca todas as datas no HTML dentro de <td> no formato dd/mm/YYYY e retorna lista de date objects."""
    try:
        resp = requests.get(URL, timeout=15)
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
        m = padrao_data.match(texto)
        if m:
            data_str = m.group(1)
            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y").date()
                datas_encontradas.append(data_obj)
            except ValueError:
                # ignora valores que não convertam por segurança
                continue

    return datas_encontradas

def main():
    datas = get_datas_da_pagina()

    if not datas:
        print("Nenhuma data no formato dd/mm/YYYY encontrada nos <td> da página.")
        return

    # imprime todas as datas encontradas (ordenadas)
    datas_ordenadas = sorted(datas)
    print("Datas encontradas (ordenadas):")
    for d in datas_ordenadas:
        print(" -", d.strftime("%d/%m/%Y"))

    maior_data_site = max(datas)
    ultima_data = ler_ultima_data()
    print(f"\nMaior data encontrada no site: {maior_data_site.strftime('%d/%m/%Y')}")
    print(f"Data presente em {ARQUIVO_DATA}: {ultima_data.strftime('%d/%m/%Y')}")

    if maior_data_site > ultima_data:
        print(">>> Há uma data no site mais recente que a do arquivo.")
        mensagem = (
            f"📢 Nova publicação detectada na Prefeitura de Cariacica:\n"
            f"<b>{maior_data_site.strftime('%d/%m/%Y')}</b>\n"
            f"Acesse: {URL}"
        )
        if ENVIAR_TELEGRAM:
            enviado = enviar_telegram(mensagem)
            print("Mensagem enviada via Telegram." if enviado else "Falha ao enviar mensagem via Telegram.")
    else:
        print("Nenhuma data mais recente encontrada no site.")

if __name__ == "__main__":
    main()
