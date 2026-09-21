import requests
import pandas as pd
import streamlit as st
import yfinance as yf

# Link do Grupo do WhatsApp do UKereno Alerts
WHATSAPP_GROUP_LINK = (
    "https://chat.whatsapp.com/K3euCPlQmNJFrnalbtPQ0R?mode=gi_t"
)

# Configuração visual da página para telemóvel
st.set_page_config(
    page_title="UKereno | Pre-Market Alerts", page_icon="📈", layout="centered"
)

# Estilo CSS estrito: Dark Mode, Botão Preto com Borda Verde, Botão WhatsApp e Métricas Maiores
st.markdown(
    """
    <style>
    /* Fundo escuro geral */
    .stApp {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }
    
    /* Título principal */
    h1 {
        font-size: 1.6rem !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.2rem !important;
    }

    /* Botão Refresh Data: Fundo Preto, Borda Verde Fina, Texto Grande */
    div.stButton > button, div.stButton > button:focus, div.stButton > button:active {
        background-color: #000000 !important;
        background: #000000 !important;
        color: #00E676 !important;
        font-size: 1.5rem !important;
        font-weight: 900 !important;
        border: 1px solid #00E676 !important;
        border-radius: 8px !important;
        padding: 0.8rem 1rem !important;
        width: 100% !important;
        box-shadow: none !important;
        outline: none !important;
    }
    div.stButton > button:hover {
        background-color: #00E676 !important;
        background: #00E676 !important;
        color: #000000 !important;
        border: 1px solid #00E676 !important;
    }

    /* Botão WhatsApp em Verde de Destaque */
    .whatsapp-btn {
        display: block;
        background-color: #25D366;
        color: #FFFFFF !important;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .whatsapp-btn:hover {
        background-color: #1EBE5D;
        color: #FFFFFF !important;
    }

    /* Ajuste do tamanho de métricas e variações */
    [data-testid="stMetricValue"] {
        color: #FAFAFA !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 1.25rem !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #B0BEC5 !important;
        font-size: 1.1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Exibe o logótipo no topo
st.image("logo.jpg", use_container_width=True)

# Botão VIP do WhatsApp no topo
st.markdown(
    f'<a href="{WHATSAPP_GROUP_LINK}" target="_blank" class="whatsapp-btn">📱 Join VIP WhatsApp Group</a>',
    unsafe_allow_html=True,
)

# Título em inglês e sub-título
st.title("📈 Pre-Market Alerts")
st.caption("Top 20 Nasdaq/NYSE stocks with ±2% minimum Gap")

# Botão de atualização
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()

st.markdown("<br>", unsafe_allow_html=True)

# Lista das 50 maiores ações ativas dos EUA
TICKERS = [
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

MIN_GAP_PCT = 2.0


@st.cache_data(ttl=300)
def carregar_dados():
    alertas = []
    for ticker in TICKERS:
        try:
            acao = yf.Ticker(ticker)
            hist = acao.history(period="2d")
            if len(hist) >= 2:
                fech_ant = hist["Close"].iloc[-2]
                preco_atual = hist["Close"].iloc[-1]
                gap = ((preco_atual - fech_ant) / fech_ant) * 100

                if abs(gap) >= MIN_GAP_PCT:
                    alertas.append({
                        "Ticker": ticker,
                        "Gap (%)": round(gap, 2),
                        "Abs_Gap": abs(gap),
                        "Preço": round(preco_atual, 2),
                        "Fech. Anterior": round(fech_ant, 2),
                    })
        except Exception:
            pass

    df = pd.DataFrame(alertas)
    if not df.empty:
        df = df.sort_values(by="Abs_Gap", ascending=False).head(20)
    return df


dados = carregar_dados()

if not dados.empty:
    for index, row in dados.iterrows():
        cor = "🟢" if row["Gap (%)"] > 0 else "🔴"
        with st.container():
            st.metric(
                label=f"{cor} {row['Ticker']}",
                value=f"${row['Preço']}",
                delta=f"{row['Gap (%)']}%",
            )
            st.write(f"Previous Close: **${row['Fech. Anterior']}**")
            st.divider()
else:
    st.info("No stocks met the ±2% Gap criteria at the moment.")

# Rodapé personalizado
st.markdown("---")
st.caption("Powered by **UKereno Global Data & Analytics**")
