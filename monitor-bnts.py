import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://www.banestes.com.br/publicacoes_legais/concurso2024.htm"
ARQUIVO_DATA = "ultima_data_bnts.txt"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def ler_ultima_data():
    try:
        with open(ARQUIVO_DATA, "r") as f:
            data_str = f.read().strip()
            return datetime.strptime(data_str, "%d/%m/%Y").date()
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
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    datas = []
    for td in soup.find_all("td", class_="dataNoticia"):
        texto = td.get_text(strip=True)
        try:
            data = datetime.strptime(texto, "%d.%m.%y").date()
            print(f"Data encontrada: {data} - texto: {texto}")
            linha = td.find_parent("tr")
            if linha:
                descricao = linha.get_text(" ", strip=True)
            else:
                descricao = "Nova publicação no site do Banestes"
            datas.append((data, descricao))
        except ValueError:
            continue

    if not datas:
        return None, None

    return max(datas, key=lambda x: x[0])

def main():
    maior_data, texto = get_maior_data()
    if maior_data is None:
        print("Nenhuma data encontrada no site.")
        return

    ultima_data = ler_ultima_data()

    if ultima_data > maior_data:
        print("Data no arquivo é mais recente que a data do site. Ignorando.")
        return

    if maior_data > ultima_data:
        mensagem = (f"🚨 Nova publicação no site do Banestes:\n<b>{maior_data.strftime('%d/%m/%Y')}</b>\n"
                    f"Descrição: {texto}\n"
                    f"Acesse: {URL}")
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
