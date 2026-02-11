import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

st.set_page_config(page_title="Market Intelligence Suite - CFTC", layout="wide")

# ===============================
# 📥 CARREGAMENTO E TRATAMENTO
# ===============================

@st.cache_data
def load_data():
    if not os.path.exists("dados_dashboard.csv"):
        return pd.DataFrame()

    df = pd.read_csv("dados_dashboard.csv")

    # Padronização
    df.columns = df.columns.str.strip()

    df["data_referencia"] = pd.to_datetime(df["data_referencia"], errors="coerce")
    df["Comprados"] = pd.to_numeric(df["Comprados"], errors="coerce").fillna(0)
    df["Vendidos"] = pd.to_numeric(df["Vendidos"], errors="coerce").fillna(0)

    # Feature Engineering
    df["Saldo_Liquido"] = df["Comprados"] - df["Vendidos"]
    df["Sentimento"] = df["Saldo_Liquido"].apply(
        lambda x: "Bullish" if x > 0 else "Bearish"
    )

    # ===============================
    # 🔎 ENRIQUECIMENTO
    # ===============================

    # Extrai código dentro do nome (ex: GOLD - CME (GC) → GC)
    def extrair_codigo(texto):
        match = re.search(r"\((.*?)\)", str(texto))
        return match.group(1) if match else "SEM_CODIGO"

    df["Codigo_Ativo"] = df["nome_ativo"].apply(extrair_codigo)

    # Separa ativo e bolsa pelo traço
    split_data = df["nome_ativo"].str.rsplit(" - ", n=1, expand=True)
    if split_data.shape[1] > 1:
        df["Ativo_Limpo"] = split_data[0]
        df["Bolsa_Origem"] = split_data[1]
    else:
        df["Ativo_Limpo"] = df["nome_ativo"]
        df["Bolsa_Origem"] = "OUTROS"

    return df.sort_values("data_referencia")


df = load_data()

if df.empty:
    st.error("Nenhum dado encontrado.")
    st.stop()

# ===============================
# 📂 SIDEBAR
# ===============================

st.sidebar.title("Navegação")

pagina = st.sidebar.radio(
    "Selecione a página:",
    ["📊 Dashboard Executivo",
     "🧪 Laboratório Estatístico",
     "📅 Análise Temporal"]
)

st.sidebar.markdown("---")
st.sidebar.header("Filtros")

# Filtro por Bolsa
bolsa = st.sidebar.selectbox(
    "Bolsa",
    ["TODAS"] + sorted(df["Bolsa_Origem"].unique())
)

if bolsa != "TODAS":
    df = df[df["Bolsa_Origem"] == bolsa]

# Filtro por Código
codigo = st.sidebar.selectbox(
    "Código do Ativo",
    ["TODOS"] + sorted(df["Codigo_Ativo"].unique())
)

if codigo != "TODOS":
    df = df[df["Codigo_Ativo"] == codigo]

# Filtro por Data
data_min = df["data_referencia"].min()
data_max = df["data_referencia"].max()

intervalo_data = st.sidebar.date_input(
    "Intervalo de Datas",
    [data_min, data_max]
)

df = df[
    (df["data_referencia"] >= pd.to_datetime(intervalo_data[0])) &
    (df["data_referencia"] <= pd.to_datetime(intervalo_data[1]))
]

# Filtro por Sentimento
sentimento = st.sidebar.multiselect(
    "Sentimento",
    options=df["Sentimento"].unique(),
    default=df["Sentimento"].unique()
)

df = df[df["Sentimento"].isin(sentimento)]

# ===============================
# 📊 DASHBOARD EXECUTIVO
# ===============================

if pagina == "📊 Dashboard Executivo":

    st.title("Dashboard Executivo")

    ultimo = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Posição Líquida Atual", f"{ultimo['Saldo_Liquido']:,.0f}")
    col2.metric("Comprados", f"{ultimo['Comprados']:,.0f}")
    col3.metric("Vendidos", f"{ultimo['Vendidos']:,.0f}")
    col4.metric("Sentimento", ultimo["Sentimento"])

    st.subheader("Tendência do Saldo Líquido")

    fig = px.line(
        df,
        x="data_referencia",
        y="Saldo_Liquido",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

# ===============================
# 🧪 LABORATÓRIO ESTATÍSTICO
# ===============================

elif pagina == "🧪 Laboratório Estatístico":

    st.title("Laboratório Estatístico")

    stats = df[["Comprados", "Vendidos", "Saldo_Liquido"]].describe().T
    stats["Mediana"] = df.median(numeric_only=True)
    stats["Moda"] = df.mode(numeric_only=True).iloc[0]
    stats["Desvio Padrão"] = df.std(numeric_only=True)

    st.subheader("Estatísticas Descritivas")
    st.dataframe(stats[["mean", "Mediana", "Moda", "Desvio Padrão", "min", "max"]])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Histograma do Saldo Líquido")
        fig_hist = px.histogram(df, x="Saldo_Liquido", nbins=30)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.subheader("Relação Comprados vs Vendidos")
        fig_scatter = px.scatter(
            df,
            x="Comprados",
            y="Vendidos",
            color="Sentimento",
            size=df["Saldo_Liquido"].abs()
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ===============================
# 📅 ANÁLISE TEMPORAL
# ===============================

elif pagina == "📅 Análise Temporal":

    st.title("Análise Temporal Avançada")

    df["Ano"] = df["data_referencia"].dt.year
    df["Mês"] = df["data_referencia"].dt.month

    resumo_mensal = df.groupby(["Ano", "Mês"])["Saldo_Liquido"].mean().reset_index()

    st.subheader("Média Mensal do Saldo Líquido")

    fig_time = px.line(
        resumo_mensal,
        x="Mês",
        y="Saldo_Liquido",
        color="Ano",
        markers=True
    )

    st.plotly_chart(fig_time, use_container_width=True)