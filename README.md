# monitor-concurso-es

Monitora o site de publicações e envia alerta via Telegram.

## ✅ Como usar

1. Crie no GitHub um novo repositório com esse conteúdo.

2. Vá em **Settings > Secrets and variables > Actions** e crie dois segredos:
   - `TELEGRAM_TOKEN`: seu token do bot
   - `TELEGRAM_CHAT_ID`: seu chat id no Telegram

3. Vá em **Actions** no repositório, clique no workflow **Verificar novas publicações** e acione manualmente, ou aguarde a execução automática (a cada 30 min).

4. Acompanhe logs no GitHub em **Actions**, caso falhe ou envie mensagem.

5. Quando quiser rodar manualmente, basta clicar em "Run workflow".

---

**Para descobrir seu `chat_id`**, veja [este guia rápido](https://www.chatidbot.com/) (se preferir).

---

Crie o repositório, copie esses arquivos, configure os segredos e já tá tudo pronto. Me avisa se quiser que eu prepare um link “template” pra você!
