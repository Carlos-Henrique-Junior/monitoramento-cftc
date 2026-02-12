import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# Configuração da página
st.set_page_config(page_title="Market Intelligence Suite - CFTC", layout="wide")

# ===============================
# 📥 CARREGAMENTO E TRATAMENTO
# ===============================

@st.cache_data
def load_data():
    if not os.path.exists("dados_dashboard.csv"):
        return pd.DataFrame()

    df = pd.read_csv("dados_dashboard.csv")

    # Padronização de colunas
    df.columns = df.columns.str.strip()

    # Conversão de Tipos
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], errors="coerce")
    df["Comprados"] = pd.to_numeric(df["Comprados"], errors="coerce").fillna(0)
    df["Vendidos"] = pd.to_numeric(df["Vendidos"], errors="coerce").fillna(0)

    # Feature Engineering (Cálculos)
    df["Saldo_Liquido"] = df["Comprados"] - df["Vendidos"]
    df["Sentimento"] = df["Saldo_Liquido"].apply(
        lambda x: "Bullish" if x > 0 else "Bearish"
    )

    # ===============================
    # 🔎 ENRIQUECIMENTO DE DADOS
    # ===============================

    # 1. Extrai código dentro do nome (ex: GOLD - CME (GC) → GC)
    def extrair_codigo(texto):
        match = re.search(r"\((.*?)\)", str(texto))
        return match.group(1) if match else "N/A"

    df["Codigo_Ativo"] = df["nome_ativo"].apply(extrair_codigo)

    # 2. Separa ativo e bolsa pelo traço " - "
    split_data = df["nome_ativo"].str.rsplit(" - ", n=1, expand=True)
    
    if split_data.shape[1] > 1:
        df["Ativo_Limpo"] = split_data[0]
        df["Bolsa_Origem"] = split_data[1]
    else:
        df["Ativo_Limpo"] = df["nome_ativo"]
        df["Bolsa_Origem"] = "OUTROS"

    return df.sort_values("data_referencia")

# Carrega os dados
df_raw = load_data()

if df_raw.empty:
    st.error("❌ Nenhum dado encontrado no arquivo CSV. Execute o ETL primeiro.")
    st.stop()

# ===============================
# 📂 SIDEBAR (NAVEGAÇÃO E FILTROS)
# ===============================

st.sidebar.title("🧭 Navegação")

pagina = st.sidebar.radio(
    "Selecione a página:",
    ["📊 Dashboard Executivo",
     "🧪 Laboratório Estatístico",
     "📅 Análise Temporal"]
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros Globais")

# --- FILTRO 1: BOLSA ---
lista_bolsas = ["TODAS"] + sorted(df_raw["Bolsa_Origem"].dropna().unique().tolist())
bolsa = st.sidebar.selectbox("Bolsa (Exchange)", lista_bolsas)

if bolsa != "TODAS":
    df = df_raw[df_raw["Bolsa_Origem"] == bolsa]
else:
    df = df_raw.copy()

# --- FILTRO 2: ATIVO (DINÂMICO) ---
# O selectbox de ativos se ajusta conforme a bolsa selecionada
lista_ativos = ["TODOS"] + sorted(df["Ativo_Limpo"].unique().tolist())
ativo_selecionado = st.sidebar.selectbox("Ativo", lista_ativos)

if ativo_selecionado != "TODOS":
    df = df[df["Ativo_Limpo"] == ativo_selecionado]

# --- FILTRO 3: DATA ---
data_min = df["data_referencia"].min()
data_max = df["data_referencia"].max()

intervalo_data = st.sidebar.date_input(
    "Intervalo de Datas",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

if len(intervalo_data) == 2:
    df = df[
        (df["data_referencia"] >= pd.to_datetime(intervalo_data[0])) &
        (df["data_referencia"] <= pd.to_datetime(intervalo_data[1]))
    ]

# --- FILTRO 4: SENTIMENTO (LÓGICA CORRIGIDA) ---
# Se o usuário limpar a lista, consideramos "TODOS" em vez de "NENHUM"
lista_sentimentos = sorted(df_raw["Sentimento"].unique().tolist())
sentimento = st.sidebar.multiselect(
    "Sentimento",
    options=lista_sentimentos,
    default=[] # Começa vazio (mostra tudo)
)

if sentimento: # Se a lista NÃO estiver vazia, aplica o filtro
    df = df[df["Sentimento"].isin(sentimento)]
# Se estiver vazia (else), não faz nada, ou seja, mostra tudo.

# ===============================
# 🚨 AIRBAG (PROTEÇÃO CONTRA ERROS)
# ===============================
if df.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados. Tente limpar os filtros.")
    st.stop() # Para a execução aqui para não dar erro lá embaixo

# ===============================
# 📊 PÁGINA 1: DASHBOARD EXECUTIVO
# ===============================

if pagina == "📊 Dashboard Executivo":

    st.title(f"📈 Monitoramento: {ativo_selecionado if ativo_selecionado != 'TODOS' else 'Visão Geral'}")
    
    # Pega o dado mais recente (com segurança, pois já checamos df.empty)
    ultimo = df.iloc[-1]

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📅 Data Ref.", ultimo['data_referencia'].strftime('%d/%m/%Y'))
    col2.metric("💰 Posição Líquida", f"{ultimo['Saldo_Liquido']:,.0f}")
    col3.metric("🟢 Comprados", f"{ultimo['Comprados']:,.0f}")
    col4.metric("🔴 Vendidos", f"{ultimo['Vendidos']:,.0f}")

    # Indicador Visual de Sentimento
    cor_sentimento = "green" if ultimo['Saldo_Liquido'] > 0 else "red"
    st.markdown(f"### Sentimento Atual: :{cor_sentimento}[{ultimo['Sentimento']}]")

    st.divider()

    st.subheader("Tendência do Saldo Líquido (Net Position)")
    fig = px.line(
        df,
        x="data_referencia",
        y="Saldo_Liquido",
        markers=True,
        title="Evolução do Posicionamento ao Longo do Tempo"
    )
    fig.update_traces(line_color='#3366CC', line_width=3)
    st.plotly_chart(fig, use_container_width=True)

# ===============================
# 🧪 PÁGINA 2: LABORATÓRIO ESTATÍSTICO
# ===============================

elif pagina == "🧪 Laboratório Estatístico":

    st.title("🔬 Laboratório Estatístico")

    # Garante que só pegamos colunas numéricas para as estatísticas
    cols_numericas = ["Comprados", "Vendidos", "Saldo_Liquido"]
    
    stats = df[cols_numericas].describe().T
    stats["Mediana"] = df[cols_numericas].median()
    stats["Desvio Padrão"] = df[cols_numericas].std()

    st.subheader("1. Estatísticas Descritivas")
    st.dataframe(stats[["mean", "Mediana", "Desvio Padrão", "min", "max"]].style.format("{:.1f}"))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("2. Distribuição (Histograma)")
        fig_hist = px.histogram(
            df, 
            x="Saldo_Liquido", 
            nbins=30,
            color_discrete_sequence=['#00CC96']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.subheader("3. Correlação (Scatter Plot)")
        
        # Cria coluna de tamanho absoluto para não dar erro no gráfico
        df["Tamanho_Absoluto"] = df["Saldo_Liquido"].abs()
        
        fig_scatter = px.scatter(
            df,
            x="Comprados",
            y="Vendidos",
            color="Sentimento",
            size="Tamanho_Absoluto", # Usa o valor positivo para o tamanho da bolinha
            hover_data=["Saldo_Liquido", "data_referencia"],
            title="Relação Comprados x Vendidos"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ===============================
# 📅 PÁGINA 3: ANÁLISE TEMPORAL
# ===============================

elif pagina == "📅 Análise Temporal":

    st.title("📅 Análise Sazonal e Temporal")

    # Extrai Mês e Ano
    df["Ano"] = df["data_referencia"].dt.year
    df["Mês"] = df["data_referencia"].dt.month

    # Agrupamento
    resumo_mensal = df.groupby(["Ano", "Mês"])["Saldo_Liquido"].mean().reset_index()

    st.subheader("Média Mensal do Saldo Líquido")
    st.info("Este gráfico ajuda a identificar sazonalidade (meses onde o ativo costuma subir ou cair).")

    fig_time = px.line(
        resumo_mensal,
        x="Mês",
        y="Saldo_Liquido",
        color="Ano",
        markers=True
    )
    # Força o eixo X a mostrar todos os meses (1 a 12)
    fig_time.update_xaxes(dtick=1)
    
    st.plotly_chart(fig_time, use_container_width=True)