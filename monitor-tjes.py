import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://www.tjes.jus.br/portal-transparencia/pessoal/contratacao-temporaria/"
ARQUIVO_DATA = "ultima_data_tjes.txt"
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
    for td in soup.find_all("td"):
        texto = td.get_text(strip=True)
        try:
            # Tenta converter para data nos formatos mais comuns
            for formato in ["%d/%m/%Y", "%d.%m.%Y", "%d/%m/%y"]:
                try:
                    data = datetime.strptime(texto, formato).date()
                    break
                except ValueError:
                    continue
            else:
                continue  # Nenhum formato bateu

            print(f"Data encontrada: {data} - texto: {texto}")
            linha = td.find_parent("tr")
            if linha:
                descricao = linha.get_text(" ", strip=True)
            else:
                descricao = "Nova publicação no site do TJES"
            datas.append((data, descricao))
        except Exception:
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
        mensagem = (f"📌 Nova publicação no site do TJES:\n<b>{maior_data.strftime('%d/%m/%Y')}</b>\n"
                    f"Acesse: {URL}")
        sucesso = enviar_telegram(mensagem)
        if sucesso:
            print("Mensagem enviada com sucesso.")
            salvar_data(maior_data)
        else:
            print("Erro ao enviar mensagem no Telegram.")
    else:
        print("Nenhuma data nova TJES.")

if __name__ == "__main__":
    main()
