import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

URL = "https://conhecimento.fgv.br/concursos/mpes26"

ARQUIVO_DATA = "dt_mpes.txt"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Data inicial para considerar publicações
DATA_MINIMA = datetime.strptime("01/08/2026", "%d/%m/%Y").date()


def ler_ultima_data():
    try:
        with open(ARQUIVO_DATA, "r") as f:
            return datetime.strptime(f.read().strip(), "%d/%m/%Y").date()
    except:
        return DATA_MINIMA


def salvar_data(data):
    with open(ARQUIVO_DATA, "w") as f:
        f.write(data.strftime("%d/%m/%Y"))


def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    resp = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
        },
    )

    return resp.ok


def get_maior_data():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    texto = soup.get_text(" ", strip=True)

    datas = []

    for match in re.findall(r"\d{2}/\d{2}/\d{4}", texto):
        try:
            data = datetime.strptime(match, "%d/%m/%Y").date()

            if data > DATA_MINIMA:
                datas.append(data)

        except:
            pass

    if not datas:
        return None

    return max(datas)


def main():

    maior_data = get_maior_data()

    if maior_data is None:
        print("Nenhuma publicação mais recente encontrada.")
        return

    ultima_data = ler_ultima_data()

    print("Última salva:", ultima_data)
    print("Maior encontrada:", maior_data)

    if maior_data > ultima_data:

        mensagem = (
            "🚨 <b>Nova publicação encontrada no concurso MPES 2026 (FGV)</b>\n\n"
            f"📅 {maior_data.strftime('%d/%m/%Y')}\n\n"
            f"{URL}"
        )

        if enviar_telegram(mensagem):
            print("Mensagem enviada.")
            salvar_data(maior_data)
        else:
            print("Erro ao enviar mensagem.")

    else:
        print("Nenhuma atualização.")


if __name__ == "__main__":
    main()
