import requests
import os

URL = "https://novo.ibgpconcursos.com.br/rest/concurso/inscricaoAberta"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

PALAVRAS_CHAVE = ["ASSEMBLEIA", "LEGISLATIVA", "ESPÍRITO SANTO", "ALES", "/ES"]

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, data=data)
    if not resp.ok:
        print("Erro ao enviar mensagem:", resp.text)
    return resp.ok

def verificar_concurso_ales():
    try:
        response = requests.get(URL)
        concursos = response.json()
    except Exception as e:
        print("Erro ao acessar API:", e)
        return []

    encontrados = []
    for concurso in concursos:
        if not concurso.get("statusInscricao"):
            continue
        nome_concurso = concurso.get("nome", "").upper()
        nome_orgao = concurso.get("empresa", {}).get("nome", "").upper()

        texto = f"{nome_concurso} - {nome_orgao}"

        if any(palavra in texto for palavra in PALAVRAS_CHAVE):
            encontrados.append(texto)

    return encontrados

def main():
    concursos_encontrados = verificar_concurso_ales()
    if concursos_encontrados:
        linhas = "\n".join(f"• {nome}" for nome in concursos_encontrados)
        mensagem = (
            "🚨 Concurso com inscrições abertas identificado para a Assembleia Legislativa do ES:\n\n"
            "🔗 <a href='https://novo.ibgpconcursos.com.br/inscricoes_abertas.jsp'>Acesse o site</a>"
        )
        enviar_telegram(mensagem)
    else:
        print("Nenhum concurso da Assembleia Legislativa do ES encontrado.")

if __name__ == "__main__":
    main()
