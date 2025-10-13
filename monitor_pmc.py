import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# === CONFIGURAÇÕES ===
URL = "https://www.cariacica.es.gov.br/documento/ver/36/detalhes"
ARQUIVO_DATA = "data_pmc.txt"

# Configurações do bot do Telegram
TELEGRAM_BOT_TOKEN = "SEU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"

# === FUNÇÃO PARA ENVIAR MENSAGEM PARA TELEGRAM ===
def enviar_mensagem_telegram(mensagem):
    url_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url_api, data=payload)
        if response.status_code == 200:
            print("📨 Mensagem enviada ao Telegram com sucesso!")
        else:
            print(f"⚠️ Falha ao enviar mensagem para Telegram: {response.status_code}")
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

# === FUNÇÃO PRINCIPAL ===
def main():
    # Ler a data do arquivo
    try:
        with open(ARQUIVO_DATA, "r", encoding="utf-8") as f:
            data_arquivo_str = f.read().strip()
            data_arquivo = datetime.strptime(data_arquivo_str, "%d/%m/%Y")
            print(f"📂 Data no arquivo: {data_arquivo_str}")
    except FileNotFoundError:
        print("⚠️ Arquivo data_pmc.txt não encontrado. Crie o arquivo com uma data no formato dd/mm/yyyy.")
        return
    except ValueError:
        print("⚠️ Data inválida no arquivo. Use o formato dd/mm/yyyy.")
        return

    # Cabeçalhos para evitar bloqueio 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://www.cariacica.es.gov.br/documento?tipo=2",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    # Acessar a página
    try:
        response = requests.get(URL, headers=headers)
        if response.status_code != 200:
            print(f"❌ Resposta HTTP {response.status_code} ao acessar {URL}")
            return
    except requests.RequestException as e:
        print("🚨 Erro de conexão:", e)
        return

    # Parse do HTML
    soup = BeautifulSoup(response.text, "html.parser")
    tds = [td.get_text(strip=True) for td in soup.find_all("td")]

    # Extrair datas
    datas = []
    for td_text in tds:
        datas_encontradas = re.findall(r"\b\d{2}/\d{2}/\d{4}\b", td_text)
        datas.extend(datas_encontradas)

    if not datas:
        print("⚠️ Nenhuma data no formato dd/mm/yyyy encontrada nos <td> da página.")
        return

    # Mostrar todas as datas encontradas
    print("\n📅 Datas encontradas na página:")
    for d in datas:
        print(" -", d)

    # Converter para datetime e comparar
    datas_convertidas = [datetime.strptime(d, "%d/%m/%Y") for d in datas]
    maior_data = max(datas_convertidas)

    print(f"\n📊 Maior data encontrada: {maior_data.strftime('%d/%m/%Y')}")

    # Comparar com data do arquivo
    if maior_data > data_arquivo:
        msg = (
            f"🚨 <b>Nova data detectada!</b>\n\n"
            f"Data anterior: {data_arquivo.strftime('%d/%m/%Y')}\n"
            f"Nova data: {maior_data.strftime('%d/%m/%Y')}\n\n"
            f"<a href='{URL}'>Ver documento</a>"
        )
        enviar_mensagem_telegram(msg)
    else:
        print("✅ Nenhuma data mais recente encontrada.")

# === EXECUÇÃO ===
if __name__ == "__main__":
    main()
