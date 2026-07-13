import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json

URL = "https://www.institutoconsulplan.org.br/Concurso/z3barr3DDJCL9q1a1xZbPKcfQ%3D%3D"

ARQUIVO = "consulplan_enviados.json"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def carregar():
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(list(dados), f, ensure_ascii=False, indent=2)


def enviar_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
    )


def buscar_publicacoes():

    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    hoje = datetime.now().strftime("%d/%m/%Y")

    publicacoes = []

    tabela = soup.find("table")

    for tr in tabela.find_all("tr"):

        tds = tr.find_all("td")

        if len(tds) < 2:
            continue

        titulo = tds[0].get_text(strip=True)

        data = tds[1].get_text(strip=True)

        if data != hoje:
            continue

        link = tds[0].find("a")["href"]

        publicacoes.append({
            "titulo": titulo,
            "data": data,
            "link": link
        })

    return publicacoes


def main():

    enviados = carregar()

    publicacoes = buscar_publicacoes()

    if not publicacoes:
        print("Nenhuma publicação hoje.")
        return

    for pub in publicacoes:

        if pub["link"] in enviados:
            continue

        mensagem = (
            "🚨 <b>Nova publicação - Consulplan</b>\n\n"
            f"<b>{pub['titulo']}</b>\n"
            f"📅 {pub['data']}\n\n"
            f"{pub['link']}"
        )

        enviar_telegram(mensagem)

        enviados.add(pub["link"])

        print("Enviado:", pub["titulo"])

    salvar(enviados)


if __name__ == "__main__":
    main()
