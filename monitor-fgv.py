import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

URL = "https://conhecimento.fgv.br/concursos/mpes26"

ARQUIVO_DATA = "dt_mpes.txt"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

DATA_MINIMA = datetime.strptime("01/08/2026", "%d/%m/%Y").date()


def ler_ultima_data():
    try:
        with open(ARQUIVO_DATA, "r") as f:
            return datetime.strptime(f.read().strip(), "%d/%m/%Y").date()
    except (FileNotFoundError, ValueError):
        return DATA_MINIMA


def salvar_data(data):
    with open(ARQUIVO_DATA, "w") as f:
        f.write(data.strftime("%d/%m/%Y"))


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML",
    }

    return requests.post(url, data=data).ok


def get_maior_data():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(URL, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    publicacoes = []

    for bloco in soup.select("div.paragraph--type--texto-data"):

        time_tag = bloco.find("time")

        if not time_tag:
            continue

        try:
            data = datetime.strptime(
                time_tag.get_text(strip=True),
                "%d/%m/%Y"
            ).date()
        except ValueError:
            continue

        if data <= DATA_MINIMA:
            continue

        campo_texto = bloco.select_one(".field--name-field-td-texto")

        if campo_texto:
            descricao = campo_texto.get_text(" ", strip=True)
        else:
            descricao = "Nova publicação"

        publicacoes.append((data, descricao))

    if not publicacoes:
        return None, None

    return max(publicacoes, key=lambda x: x[0])


def main():

    maior_data, descricao = get_maior_data()

    if maior_data is None:
        print("Nenhuma publicação encontrada.")
        return

    ultima_data = ler_ultima_data()

    if ultima_data > maior_data:
        print("Data do arquivo é mais recente.")
        return

    if maior_data > ultima_data:

        mensagem = (
            "🚨 <b>Nova publicação no concurso MPES 2026 (FGV)</b>\n\n"
            f"📅 <b>{maior_data.strftime('%d/%m/%Y')}</b>\n"
            f"📄 {descricao}\n\n"
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
