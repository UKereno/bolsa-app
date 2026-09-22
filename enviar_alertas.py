import os
import requests
import yfinance as yf

# Configurações da Z-API
INSTANCE_ID = os.environ.get("ZAPI_INSTANCE_ID")
TOKEN = os.environ.get("ZAPI_TOKEN")
CLIENT_TOKEN = os.environ.get("ZAPI_CLIENT_TOKEN")

# Cole aqui o ID numérico do seu grupo do WhatsApp
GROUP_ID = "120363XXXXXXXXXX@g.us" 

HEADERS = {
    "Client-Token": CLIENT_TOKEN,
    "Content-Type": "application/json"
}

def enviar_mensagem(phone, texto):
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/send-text"
    payload = {
        "phone": phone,
        "message": texto
    }
    res = requests.post(url, json=payload, headers=HEADERS)
    print(f"Status do envio: {res.status_code}")
    print(f"Resposta da Z-API: {res.text}")

def main():
    tickers = {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "FTSE 100": "^FTSE"}
    linhas = ["📊 *ALERTAS DE PRE-MARKET UKereno*\n"]

    for nome, ticker in tickers.items():
        try:
            dados = yf.Ticker(ticker).history(period="2d")
            if len(dados) >= 2:
                fech_anterior = dados['Close'].iloc[-2]
                atual = dados['Close'].iloc[-1]
                var = ((atual - fech_anterior) / fech_anterior) * 100
                sinal = "+" if var >= 0 else ""
                linhas.append(f"• *{nome}*: {atual:.2f} ({sinal}{var:.2f}%)")
        except Exception as e:
            print(f"Erro no ticker {nome}: {e}")

    mensagem = "\n".join(linhas)
    enviar_mensagem(GROUP_ID, mensagem)

if __name__ == "__main__":
    main()
