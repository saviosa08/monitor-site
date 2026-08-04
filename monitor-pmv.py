import requests
import re
from datetime import datetime
import os
from bs4 import BeautifulSoup

URL = "https://www.institutoconsulplan.org.br/OC2XhfaSAlbarrSPiDfhMQqHA=="

ARQUIVO_DATA = "ultima_data_pmv.txt"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def ler_ultima_data():
    try:
        with open(ARQUIVO_DATA, "r") as f:
            return datetime.strptime(f.read().strip(), "%d/%m/%Y").date()
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

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(URL, headers=headers, timeout=30)

    print("Status:", resp.status_code)

    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    datas = []

    # percorre todos os links da página
    for a in soup.find_all("a"):

        texto = a.get_text(strip=True)

        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", texto):

            try:
                data = datetime.strptime(texto, "%d/%m/%Y").date()
                print("Data encontrada:", data)
                datas.append(data)
            except ValueError:
                pass

    if not datas:
        print("Nenhuma data encontrada.")
        return None

    print("Maior data:", max(datas))

    return max(datas)


def main():

    maior_data = get_maior_data()
    # maior_data = datetime.strptime("10/07/2026", "%d/%m/%Y").date()

    if maior_data is None:
        print("Não foi possível localizar nenhuma data.")
        return

    ultima_data = ler_ultima_data()

    print(f"Última data salva: {ultima_data}")
    print(f"Maior data encontrada: {maior_data}")

    if ultima_data > maior_data:
        print("Data salva é maior que a do site.")
        return

    if maior_data > ultima_data:

        mensagem = (
            "🚨 <b>Nova publicação no site da Consulplan</b>\n\n"
            f"<b>{maior_data.strftime('%d/%m/%Y')}</b>\n"
            f"{URL}"
        )

        if enviar_telegram(mensagem):
            print("Mensagem enviada.")
            salvar_data(maior_data)
        else:
            print("Erro ao enviar Telegram.")

    else:
        print("Nenhuma data nova.")


if __name__ == "__main__":
    main()
