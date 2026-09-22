import os
import requests
import yfinance as yf

# Configurações da Z-API
INSTANCE_ID = os.environ.get("ZAPI_INSTANCE_ID")
TOKEN = os.environ.get("ZAPI_TOKEN")
CLIENT_TOKEN = os.environ.get("ZAPI_CLIENT_TOKEN")

HEADERS = {
    "Client-Token": CLIENT_TOKEN,
    "Content-Type": "application/json"
}

def obter_id_do_grupo():
    # Procura o ID do grupo na lista de chats ativos
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/chats"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            chats = response.json()
            for chat in chats:
                name = chat.get("name", "") or chat.get("phone", "")
                if "UKereno" in name or "Pre-Market" in name:
                    return chat.get("phone") or chat.get("id")
    except Exception as e:
        print(f"Erro ao procurar chats: {e}")
    
    # Caso não encontre na lista, usa o convite de grupo
    url_invite = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/group-metadata/K3euCPlQmNJFrnalbtPQ0R"
    try:
        res = requests.get(url_invite, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("phone")
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
    print(f"Resposta da Z-API: {res.text}")

def main():
    group_id = obter_id_do_grupo()
    if not group_id:
        print("Não foi possível localizar o ID do grupo UKereno Pre-Market VIP.")
        return

    print(f"Grupo localizado com sucesso: {group_id}")

    # Coleta de dados simples para teste
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
            print(f"Erro ao buscar {nome}: {e}")

    mensagem = "\n".join(linhas)
    enviar_mensagem(group_id, mensagem)

if __name__ == "__main__":
    main()
