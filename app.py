import pandas as pd
import streamlit as st
import yfinance as yf

# Configuração visual para ecrã de telemóvel
st.set_page_config(
    page_title="UKereno | Alertas Bolsa",
    page_icon="📈",
    layout="centered"
)

# Estilização em CSS para forçar o fundo preto/escuro e ajustar cores
st.markdown(
    """
    <style>
    /* Fundo da aplicação */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Estilo do título das métricas */
    [data-testid="stMetricValue"] {
        color: #FAFAFA !important;
    }
    [data-testid="stMetricLabel"] {
        color: #B0BEC5 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Exibe o logótipo centralizado no topo do app
st.image("logo.jpg", use_container_width=True)

st.title("📈 Alertas Pré-Mercado")
st.caption("Monitorização de ações Nasdaq/NYSE com variação mínima de ±2%")

# Botão para atualizar dados manualmente
if st.button("🔄 Atualizar Dados", use_container_width=True):
    st.cache_data.clear()

# Lista de ativos para monitorizar
TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMD", "TSLA",
    "AMZN", "GOOGL", "META", "NFLX", "INTC"
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
            st.write(f"Fechamento anterior: **${row['Fech. Anterior']}**")
            st.divider()
else:
    st.info("Nenhum ativo atingiu o critério de ±2% de Gap no momento.")

# Rodapé com a marca
st.markdown("---")
st.caption("Powered by **UKereno Analytics**")
