import pandas as pd
import streamlit as st
import yfinance as yf

# Link do Grupo do WhatsApp do UKereno Alerts
WHATSAPP_GROUP_LINK = (
    "https://chat.whatsapp.com/K3euCPlQmNJFrnalbtPQ0R?mode=gi_t"
)

# Configuração visual da página
st.set_page_config(
    page_title="UKereno | Global Market Alerts", page_icon="📈", layout="centered"
)

# Estilo CSS avançado: Dark Mode, Botão WhatsApp Discreto (Preto sem Borda), Botão Refresh e Abas Estilizadas
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

    /* Botão WhatsApp Discreto */
    .whatsapp-btn {
        display: block;
        background-color: #0E1117 !important;
        color: #25D366 !important;
        text-align: center;
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
        border-radius: 8px !important;
        text-decoration: none !important;
        margin-bottom: 1.2rem !important;
        transition: all 0.2s ease !important;
    }
    .whatsapp-btn:hover {
        background-color: #161B22 !important;
        color: #00E676 !important;
    }

    /* Botão Refresh Data: Fundo Preto, Borda Verde Fina */
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

    /* Estilo das Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161B22 !important;
        border-radius: 6px !important;
        color: #B0BEC5 !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00E676 !important;
        color: #000000 !important;
    }

    /* Ajuste de métricas */
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
try:
    st.image("logo.jpg", use_container_width=True)
except Exception:
    pass

# Botão discreto do WhatsApp
st.markdown(
    f'<a href="{WHATSAPP_GROUP_LINK}" target="_blank" class="whatsapp-btn">💬 Join VIP WhatsApp Group</a>',
    unsafe_allow_html=True,
)

# Título em inglês e sub-título
st.title("📈 UKereno Global Market Alerts")
st.caption("Top Movers with ±2% Minimum Gap Across Global Markets")

# Botão de atualização
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()

st.markdown("<br>", unsafe_allow_html=True)

# Listas de Tickers por Região
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

UK_EU_TICKERS = [
    "SHEL.L",
    "AZN.L",
    "HSBA.L",
    "BP.L",
    "RIO.L",
    "GSK.L",
    "ULVR.L",
    "REL.L",
    "BATS.L",
    "PRU.L",
    "SAP.DE",
    "ASML.AS",
    "TTE.PA",
    "MC.PA",
    "OR.PA",
    "SIE.DE",
]

BR_TICKERS = [
    "PETR4.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "BBDC4.SA",
    "BBAS3.SA",
    "ABEV3.SA",
    "WEGE3.SA",
    "RENT3.SA",
    "PRIO3.SA",
    "ELET3.SA",
    "GGBR4.SA",
    "CSNA3.SA",
    "SUZB3.SA",
    "JBSS3.SA",
    "MGLU3.SA",
    "B3SA3.SA",
]

MIN_GAP_PCT = 2.0


@st.cache_data(ttl=300)
def carregar_dados_lote(tickers_list):
    alertas = []
    try:
        # Download de todas as ações em batch de uma só vez (muito mais rápido e sem travar)
        dados = yf.download(
            tickers_list, period="5d", progress=False, group_by="ticker"
        )

        for ticker in tickers_list:
            try:
                if len(tickers_list) == 1:
                    df_ticker = dados
                else:
                    df_ticker = dados[ticker]

                df_clean = df_ticker.dropna(subset=["Close"])

                if len(df_clean) >= 2:
                    fech_ant = float(df_clean["Close"].iloc[-2])
                    preco_atual = float(df_clean["Close"].iloc[-1])

                    if fech_ant > 0:
                        gap = ((preco_atual - fech_ant) / fech_ant) * 100

                        if abs(gap) >= MIN_GAP_PCT:
                            ticker_clean = ticker.split(".")[0]
                            alertas.append({
                                "Ticker": ticker_clean,
                                "Gap (%)": round(gap, 2),
                                "Abs_Gap": abs(gap),
                                "Preço": round(preco_atual, 2),
                                "Fech. Anterior": round(fech_ant, 2),
                            })
            except Exception:
                continue
    except Exception:
        pass

    df_resultado = pd.DataFrame(alertas)
    if not df_resultado.empty:
        df_resultado = df_resultado.sort_values(
            by="Abs_Gap", ascending=False
        ).head(20)
    return df_resultado


def exibir_alertas(df):
    if df is not None and not df.empty:
        for index, row in df.iterrows():
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
        st.info("No stocks met the ±2% Gap criteria in this market right now.")


# Criação das Abas no App
tab_us, tab_uk_eu, tab_br = st.tabs(
    ["🇺🇸 US Pre-Market", "🇬🇧 UK & Europe", "🇧🇷 Brasil (B3)"]
)

with tab_us:
    dados_us = carregar_dados_lote(US_TICKERS)
    exibir_alertas(dados_us)

with tab_uk_eu:
    dados_uk_eu = carregar_dados_lote(UK_EU_TICKERS)
    exibir_alertas(dados_uk_eu)

with tab_br:
    dados_br = carregar_dados_lote(BR_TICKERS)
    exibir_alertas(dados_br)

# Rodapé personalizado
st.markdown("---")
st.caption("Powered by **UKereno Global Data & Analytics**")
