import os
import requests
import yfinance as yf
import pandas as pd

# Credenciais da Z-API obtidas das Secrets do GitHub
INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
TOKEN = os.getenv("ZAPI_TOKEN")
CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
INVITE_CODE = "K3euCPlQmNJFrnalbtPQ0R"

# Lista simplificada para o alerta diário via WhatsApp
US_TICKERS = ["AAPL", "MSFT", "NVDA", "AMD", "TSLA", "AMZN", "GOOGL", "META", "PBR", "VALE"]
BR_TICKERS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "EMBR3.SA"]

def obter_id_grupo_via_convite():
    """Obtém o ID do grupo do WhatsApp utilizando o código do link de convite."""
    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/group-invite-info"
    headers = {"Client-Token": CLIENT_TOKEN, "Content-Type": "application/json"}
    payload = {"inviteCode": INVITE_CODE}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            dados = response.json()
            return dados.get("id") or dados.get("phone")
        print(f"Erro ao obter ID do grupo via convite: {response.text}")
    except Exception as e:
        print(f"Exceção ao ligar à Z-API: {e}")
    return None

def buscar_top_movers(tickers_list, min_gap=2.0):
    """Procura ações com variação (gap) mínima de ±2%."""
    alertas = []
    try:
        dados = yf.download(tickers_list, period="5d", progress=False, group_by="ticker")
        for ticker in tickers_list:
            try:
                df_ticker = dados if len(tickers_list) == 1 else dados.get(ticker)
                if isinstance(df_ticker, pd.DataFrame) and "Close" in df_ticker:
                    df_clean = df_ticker.dropna(subset=["Close"])
                    if len(df_clean) >= 2:
                        fech_ant = float(df_clean["Close"].iloc[-2])
                        preco_atual = float(df_clean["Close"].iloc[-1])
                        if fech_ant > 0:
                            gap = ((preco_atual - fech_ant) / fech_ant) * 100
                            if abs(gap) >= min_gap:
                                ticker_clean = ticker.split(".")[0]
                                alertas.append((ticker_clean, round(gap, 2), round(preco_atual, 2)))
            except Exception:
                continue
    except Exception as e:
        print(f"Erro ao descarregar dados: {e}")
    return alertas

def formatar_mensagem_alerta():
    """Monta a mensagem formatada para o WhatsApp."""
    alertas_us = buscar_top_movers(US_TICKERS)
    alertas_br = buscar_top_movers(BR_TICKERS)
    
    if not alertas_us and not alertas_br:
        return None

    msg = "📈 *UKereno Global Market Alerts*\n"
    msg += "🚀 *Top Movers (Gap >= ±2%)*\n\n"

    if alertas_us:
        msg += "🇺🇸 *EUA / NYSE / NASDAQ:*\n"
        for ticker, gap, preco in alertas_us:
            sinal = "🟢" if gap > 0 else "🔴"
            msg += f"{sinal} *{ticker}*: {gap}% (Preço: ${preco})\n"
        msg += "\n"

    if alertas_br:
        msg += "🇧🇷 *Brasil / B3:*\n"
        for ticker, gap, preco in alertas_br:
            sinal = "🟢" if gap > 0 else "🔴"
            msg += f"{sinal} *{ticker}*: {gap}% (Preço: R${preco})\n"
        msg += "\n"

    msg += "📊 Aceda ao painel completo: https://share.streamlit.io/"
    return msg

def enviar_alerta_whatsapp():
    group_id = obter_id_grupo_via_convite()
    if not group_id:
        print("Cancelado: ID do grupo não encontrado.")
        return

    mensagem = formatar_mensagem_alerta()
    if not mensagem:
        mensagem = "📊 *UKereno Alerts*: Nenhum ativo atingiu a variação mínima de ±2% no mercado neste momento."

    url = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/send-text"
    headers = {
        "Client-Token": CLIENT_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "phone": group_id,
        "message": mensagem
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print("Status do envio:", response.status_code)
    print("Resposta da Z-API:", response.text)

if __name__ == "__main__":
    enviar_alerta_whatsapp()
