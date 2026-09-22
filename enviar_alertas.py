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

def listar_e_encontrar_grupo():
    # Consulta a lista de chats da instância
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/chats"
    print("Consultando lista de chats...")
    
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            chats = response.json()
            print(f"Total de chats encontrados: {len(chats)}")
            
            for chat in chats:
                nome = chat.get("name") or chat.get("phone") or "Sem Nome"
                chat_id = chat.get("phone") or chat.get("id")
                print(f"-> Chat: '{nome}' | ID: {chat_id}")
                
                # Procura por palavras-chave do seu grupo
                if "UKereno" in str(nome) or "Pre-Market" in str(nome) or "VIP" in str(nome):
                    print(f"\n✅ GRUPO ENCONTRADO: {nome} -> ID: {chat_id}\n")
                    return chat_id
        else:
            print(f"Erro ao listar chats: {response.text}")
            
    except Exception as e:
        print(f"Exceção durante a busca: {e}")
        
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
    group_id = listar_e_encontrar_grupo()
    
    if not group_id:
        print("\n❌ Grupo não localizado automaticamente na lista acima.")
        return

    # Busca cotações dos índices
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
