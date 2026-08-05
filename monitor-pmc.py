import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

URL = "https://cariacica.es.gov.br/documento/ver/36/detalhes"
ARQUIVO_DATA = "ultima_data_pmc.txt"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def ler_ultima_data():
    try:
        with open(ARQUIVO_DATA, "r") as f:
            return datetime.strptime(f.read().strip(), "%d/%m/%Y").date()
    except (FileNotFoundError, ValueError):
        return datetime.min.date()


# def salvar_data(data):
#     with open(ARQUIVO_DATA, "w") as f:
#         f.write(data.strftime("%d/%m/%Y"))


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    resp = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensagem,
            "parse_mode": "HTML",
        },
        timeout=30,
    )

    return resp.ok


def get_maior_data():

    session = requests.Session()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
        "Referer": "https://cariacica.es.gov.br/",
    }

    # Obtém cookies
    session.get(
        "https://cariacica.es.gov.br/",
        headers=headers,
        timeout=30,
    )

    resp = session.get(
        URL,
        headers=headers,
        timeout=30,
    )

    print("=" * 80)
    print("Status:", resp.status_code)
    print("URL Final:", resp.url)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("=" * 80)

    resp.raise_for_status()

    # Salva exatamente o HTML recebido
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(resp.text)

    soup = BeautifulSoup(resp.text, "html.parser")

    tabelas = soup.find_all("table")
    print(f"Foram encontradas {len(tabelas)} tabela(s).")

    # Procura pela tabela desejada
    tabela = soup.select_one("table.table-anexos")

    if tabela is None:
        print("Tabela 'table-anexos' não encontrada.")

        print("\nClasses das tabelas encontradas:\n")
        for i, t in enumerate(tabelas, start=1):
            print(f"Tabela {i}: {t.get('class')}")

        print("\nPrimeiros 3000 caracteres do HTML recebido:\n")
        print(resp.text[:3000])

        return None, None

    tbody = tabela.find("tbody")

    if tbody is None:
        print("tbody não encontrado.")
        return None, None

    datas = []

    for tr in tbody.find_all("tr"):

        tds = tr.find_all("td")

        if len(tds) < 2:
            continue

        descricao = tds[0].get_text(" ", strip=True)
        data_str = tds[1].get_text(strip=True)

        try:
            data = datetime.strptime(data_str, "%d/%m/%Y").date()

            print(f"{data} -> {descricao}")

            datas.append((data, descricao))

        except ValueError:
            continue

    if not datas:
        print("Nenhuma data válida encontrada.")
        return None, None

    maior_data, descricao = max(datas, key=lambda x: x[0])

    print("\nMaior data:", maior_data)
    print("Documento:", descricao)

    return maior_data, descricao


def main():

    maior_data, descricao = get_maior_data()

    if maior_data is None:
        print("Nenhuma data encontrada.")
        return

    ultima_data = ler_ultima_data()

    print("Última data salva :", ultima_data)
    print("Maior data do site:", maior_data)

    if ultima_data > maior_data:
        print("Data do arquivo é mais recente.")
        return

    if maior_data > ultima_data:

        mensagem = (
            f"🚨 <b>Nova publicação - Prefeitura de Cariacica</b>\n\n"
            f"<b>Data:</b> {maior_data.strftime('%d/%m/%Y')}\n"
            f"<b>Documento:</b> {descricao}\n\n"
            f"{URL}"
        )

        if enviar_telegram(mensagem):
            print("Mensagem enviada.")
            # salvar_data(maior_data)
        else:
            print("Erro ao enviar mensagem.")

    else:
        print("Nenhuma data nova.")


if __name__ == "__main__":
    main()
