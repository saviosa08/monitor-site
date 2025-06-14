import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

ARQUIVO_DATA = "ultima_data.txt"
URL = "https://selecao.es.gov.br/PaginaConcurso/Index/659"

def ler_ultima_data():
    if not os.path.exists(ARQUIVO_DATA):
        return datetime.min.date()  # retorna a menor data possível (só date)
    with open(ARQUIVO_DATA, "r") as f:
        conteudo = f.read().strip()
        return datetime.strptime(conteudo, "%d/%m/%Y").date()  # só data

def salvar_nova_data(data):
    with open(ARQUIVO_DATA, "w") as f:
        f.write(data.strftime("%d/%m/%Y"))  # grava só a data

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    response = requests.post(url, data=data)
    return response.status_code == 200

def buscar_datas_publicacoes():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    datas = []
    for div in soup.find_all("div", class_="panel panel-default"):
        data_div = div.find("div", class_="panel-heading")
        if data_div:
            texto = data_div.text.strip()
            try:
                data_str = texto.split("-")[-1].strip().split(" ")[0]  # pega só o dia/mês/ano, ignora hora
                data = datetime.strptime(data_str, "%d/%m/%Y").date()  # só data
                datas.append((data, texto))
            except ValueError:
                continue
    return datas

def main():
    ultima_data = ler_ultima_data()
    novas_publicacoes = []

    for data, texto in buscar_datas_publicacoes():
        if data > ultima_data:
            novas_publicacoes.append((data, texto))

    if novas_publicacoes:
        nova_data = max(data for data, _ in novas_publicacoes)
        mensagem = "🚨 Novas publicações encontradas no site da seleção:\n\n"
        for _, texto in novas_publicacoes:
            mensagem += f"📌 {texto}\n"
        mensagem += f"\n🔗 <a href='{URL}'>Acesse aqui</a>"
        if enviar_telegram(mensagem):
            print("Mensagem enviada com sucesso.")
        else:
            print("Erro ao enviar mensagem no Telegram.")
        salvar_nova_data(nova_data)
    else:
        print("Nenhuma nova publicação encontrada.")

if __name__ == "__main__":
    main()
