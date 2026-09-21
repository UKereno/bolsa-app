import pandas as pd
import streamlit as st
import yfinance as yf

# Configuração visual da página para telemóvel
st.set_page_config(
    page_title="UKereno | Pre-Market Alerts", page_icon="📈", layout="centered"
)

# Estilo CSS para fundo escuro e ajuste de tamanho das fontes
st.markdown(
    """
    <style>
    /* Fundo escuro */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Reduzir o tamanho do título principal */
    h1 {
        font-size: 1.6rem !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.2rem !important;
    }
    /* Estilo do valor e rótulo das métricas */
    [data-testid="stMetricValue"] {
        color: #FAFAFA !important;
    }
    [data-testid="stMetricLabel"] {
        color: #B0BEC5 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Exibe o logótipo no topo
st.image("logo.jpg", use_container_width=True)

# Título em inglês e tamanho ajustado
st.title("📈 Pre-Market Alerts")
st.caption("Monitoring Nasdaq/NYSE stocks with ±2% minimum Gap")

# Botão para atualizar dados manualmente
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()

# Lista de ações monitorizadas
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
                        "Preço": round(preco_atual, 2),
                        "Fech. Anterior": round(fech_ant, 2),
                    })
        except Exception:
            pass
    return pd.DataFrame(alertas)


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
