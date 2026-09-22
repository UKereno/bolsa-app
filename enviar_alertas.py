import os
import requests
import yfinance as yf

# Configurações da Z-API
INSTANCE_ID = os.environ.get("ZAPI_INSTANCE_ID")
TOKEN = os.environ.get("ZAPI_TOKEN")

HEADERS = {
    "Content-Type": "application/json"
}

def obter_id_do_grupo():
    # 1. Tenta encontrar o grupo na lista de chats ativos
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/chats"
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status busca chats: {response.status_code}")
        if response.status_code == 200:
            chats = response.json()
            for chat in chats:
                name = str(chat.get("name", "")) or str(chat.get("phone", ""))
                if "UKereno" in name or "Pre-Market" in name:
                    group_phone = chat.get("phone") or chat.get("id")
                    print(f"Grupo localizado: {name} ({group_phone})")
                    return group_phone
    except Exception as e:
        print(f"Erro ao buscar nos chats: {e}")

    # 2. Tenta via link/metadados de convite caso não esteja na lista de chats
    url_invite = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/group-metadata/K3euCPlQmNJFrnalbtPQ0R"
    try:
        res = requests.get(url_invite, headers=HEADERS)
        print(f"Status busca convite: {res.status_code}")
        if res.status_code == 200:
            return res.json().get("phone") or res.json().get("id")
    except Exception as e:
        print(f"Erro ao consultar convite: {e}")

    return None

def enviar_mensagem(phone, texto):
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/send-text"
    payload = {
        "phone": phone,
        "message": texto
    }
    res = requests.post(url, json=payload, headers=HEADERS)
    print(f"Status do envio: {res.status_code}")
    print(f"Resposta do envio: {res.text}")

def main():
    group_id = obter_id_do_grupo()
    if not group_id:
        print("Não foi possível identificar o ID do grupo.")
        return

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
    enviar_mensagem(group_id, mensagem)

if __name__ == "__main__":
    main()
