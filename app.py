import os
import pandas as pd
import requests
import yfinance as yf

# Variáveis de Ambiente obtidas via Secrets do GitHub
API_URL = os.getenv("EVOLUTION_API_URL")
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE", "UKerenoAlerts")
GROUP_JID = os.getenv("WHATSAPP_GROUP_ID")

# Listas de Tickers
US_TICKERS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMD",
    "TSLA",
    "AMZN",
    "GOOGL",
    "META",
    "NFLX",
    "INTC",
    "SMCI",
    "PLTR",
    "AVGO",
    "QCOM",
    "ARM",
    "MU",
    "PYPL",
    "SQ",
    "COIN",
    "MARA",
    "BAC",
    "JPM",
    "C",
    "GS",
    "MS",
    "XOM",
    "CVX",
    "PBR",
    "VALE",
    "NKE",
    "DIS",
    "SBUX",
    "BABA",
    "PDD",
    "JD",
    "NIO",
    "LI",
    "XPEV",
    "MRNA",
    "BNTX",
    "PFE",
    "LLY",
    "NVO",
    "UNH",
    "UBER",
    "ABNB",
    "DASH",
    "SPOT",
    "SHOP",
    "CRWD",
]


def buscar_gaps(tickers_list):
    alertas = []
    try:
        dados = yf.download(
            tickers_list, period="5d", progress=False, group_by="ticker"
        )
        for ticker in tickers_list:
            try:
                df_ticker = dados[ticker] if len(tickers_list) > 1 else dados
                if isinstance(df_ticker, pd.DataFrame) and "Close" in df_ticker:
                    df_clean = df_ticker.dropna(subset=["Close"])
                    if len(df_clean) >= 2:
                        fech_ant = float(df_clean["Close"].iloc[-2])
                        preco_atual = float(df_clean["Close"].iloc[-1])
                        if fech_ant > 0:
                            gap = ((preco_atual - fech_ant) / fech_ant) * 100
                            if abs(gap) >= 2.0:
                                alertas.append({
                                    "Ticker": ticker,
                                    "Gap": round(gap, 2),
                                    "Preco": round(preco_atual, 2),
                                    "Fech": round(fech_ant, 2),
                                })
            except Exception:
                continue
    except Exception:
        pass

    df_resultado = pd.DataFrame(alertas)
    if not df_resultado.empty:
        df_resultado["Abs_Gap"] = df_resultado["Gap"].abs()
        df_resultado = df_resultado.sort_values(
            by="Abs_Gap", ascending=False
        ).head(15)
    return df_resultado


def enviar_whatsapp(mensagem):
    endpoint = f"{API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    payload = {
        "number": GROUP_JID,
        "options": {"delay": 1200, "presence": "composing"},
        "textMessage": {"text": mensagem},
    }
    response = requests.post(endpoint, json=payload, headers=headers)
    return response.status_code in [200, 201]


# Execução do Alerta
df_us = buscar_gaps(US_TICKERS)

if not df_us.empty:
    msg = "🚨 *UKereno Market Alerts - US NYSE* 🚨\n\n"
    for _, row in df_us.iterrows():
        cor = "🟢" if row["Gap"] > 0 else "🔴"
        sinal = "+" if row["Gap"] > 0 else ""
        msg += f"{cor} *{row['Ticker']}*: {sinal}{row['Gap']}%\n   ├ Preço: ${row['Preco']}\n   └ Fech. Anterior: ${row['Fech']}\n\n"

    msg += "📈 *Acesse o Dashboard completo:* https://bolsa-app.streamlit.app\n"
    msg += "👉 *Grupo VIP:* https://chat.whatsapp.com/K3euCPlQmNJFrnalbtPQ0R"

    enviar_whatsapp(msg)
    print("✅ Alerta enviado com sucesso!")
else:
    print("ℹ️ Nenhum gap significativo encontrado.")
