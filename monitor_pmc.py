import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://cariacica.es.gov.br/documento/ver/36/detalhes"
ARQUIVO_DATA = "ultima_data_pmc.txt"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def ler_ultima_data():
    try:
        with open(ARQUIVO_DATA, "r") as f:
            data_str = f.read().strip()
            return datetime.strptime(data_str, "%d/%m/%Y").date()
    except (FileNotFoundError, ValueError):
        return datetime.min.date()


# def salvar_data(data):
#     with open(ARQUIVO_DATA, "w") as f:
#         f.write(data.strftime("%d/%m/%Y"))


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

    resp = requests.get(URL, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    tabela = soup.find("table", class_="table-anexos")

    if not tabela:
        return None, None

    tbody = tabela.find("tbody")

    if not tbody:
        return None, None

    datas = []

    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")

        # Esperado:
        # td[0] = descrição
        # td[1] = data
        # td[2] = botão visualizar
        if len(tds) < 2:
            continue

        descricao = tds[0].get_text(" ", strip=True)
        data_str = tds[1].get_text(strip=True)

        try:
            data = datetime.strptime(data_str, "%d/%m/%Y").date()

            print(f"Data encontrada: {data} - {descricao}")

            datas.append((data, descricao))

        except ValueError:
            continue

    if not datas:
        return None, None

    return max(datas, key=lambda x: x[0])


def main():
    maior_data, descricao = get_maior_data()

    if maior_data is None:
        print("Nenhuma data encontrada no site.")
        return

    ultima_data = ler_ultima_data()

    if ultima_data > maior_data:
        print("Data no arquivo é mais recente que a data do site. Ignorando.")
        return

    if maior_data > ultima_data:
        mensagem = (
            f"🚨 <b>Nova publicação - Prefeitura de Cariacica</b>\n\n"
            f"<b>Data:</b> {maior_data.strftime('%d/%m/%Y')}\n"
            f"<b>Documento:</b> {descricao}\n\n"
            f"Acesse: {URL}"
        )

        sucesso = enviar_telegram(mensagem)

        if sucesso:
            print("Mensagem enviada com sucesso.")
            salvar_data(maior_data)
        else:
            print("Erro ao enviar mensagem no Telegram.")

    else:
        print("Nenhuma data nova.")


if __name__ == "__main__":
    main()
