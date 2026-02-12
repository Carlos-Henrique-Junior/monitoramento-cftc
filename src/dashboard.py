import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# ===============================
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(page_title="Monitoramento CFTC - Master", layout="wide")

# ===============================
# 🧠 BUSINESS LAYER (TRADUÇÃO & INTELIGÊNCIA)
# ===============================

# 1. Dicionário de Tradução (Inglês Técnico -> Português Amigável)
def traduzir_nome_amigavel(nome_tecnico):
    nome = nome_tecnico.upper()
    
    # CRIPTO
    if 'BITCOIN' in nome: return 'Bitcoin (BTC)'
    if 'ETHER' in nome: return 'Ethereum (ETH)'
    
    # MOEDAS (FOREX)
    if 'BRAZILIAN REAL' in nome: return 'Real Brasileiro (BRL)'
    if 'EURO FX' in nome: return 'Euro (EUR)'
    if 'JAPANESE YEN' in nome: return 'Iene Japonês (JPY)'
    if 'BRITISH POUND' in nome: return 'Libra Esterlina (GBP)'
    if 'CANADIAN DOLLAR' in nome: return 'Dólar Canadense (CAD)'
    if 'DOLLAR INDEX' in nome: return 'Dólar Index (DXY)'
    if 'MEXICAN PESO' in nome: return 'Peso Mexicano (MXN)'
    
    # ÍNDICES
    if 'S&P 500' in nome: return 'S&P 500 (EUA)'
    if 'NASDAQ' in nome: return 'Nasdaq 100 (Tech)'
    if 'DOW JONES' in nome: return 'Dow Jones (Industrial)'
    if 'NIKKEI' in nome: return 'Nikkei 225 (Japão)'
    if 'VIX' in nome: return 'VIX (Índice do Medo)'
    
    # ENERGIA
    if 'CRUDE OIL' in nome and 'LIGHT' in nome: return 'Petróleo WTI'
    if 'BRENT' in nome: return 'Petróleo Brent'
    if 'NATURAL GAS' in nome: return 'Gás Natural'
    
    # METAIS
    if 'GOLD' in nome: return 'Ouro'
    if 'SILVER' in nome: return 'Prata'
    if 'COPPER' in nome: return 'Cobre'
    if 'PLATINUM' in nome: return 'Platina'
    
    # AGRÍCOLA
    if 'SOYBEAN' in nome and 'OIL' not in nome: return 'Soja (Grão)'
    if 'CORN' in nome: return 'Milho'
    if 'WHEAT' in nome: return 'Trigo'
    if 'COFFEE' in nome: return 'Café Arábica'
    if 'SUGAR' in nome: return 'Açúcar'
    if 'CATTLE' in nome: return 'Boi Gordo'
    
    # JUROS
    if '10-YEAR U.S. TREASURY' in nome: return 'Treasuries 10 Anos (EUA)'
    
    return nome.split(" - ")[0].title()

# 2. Classificação Automática de Setores
def classificar_setor(nome_amigavel):
    nome = nome_amigavel.upper()
    if any(x in nome for x in ['BITCOIN', 'ETHEREUM']): return 'Criptoativos ₿'
    if any(x in nome for x in ['S&P', 'NASDAQ', 'DOW', 'NIKKEI', 'VIX']): return 'Índices 📊'
    if any(x in nome for x in ['OURO', 'PRATA', 'COBRE', 'PLATINA']): return 'Metais ⛏️'
    if any(x in nome for x in ['PETRÓLEO', 'GÁS']): return 'Energia ⚡'
    if any(x in nome for x in ['REAL', 'EURO', 'LIBRA', 'IENE', 'DÓLAR', 'PESO']): return 'Moedas 💱'
    if any(x in nome for x in ['SOJA', 'MILHO', 'TRIGO', 'CAFÉ', 'AÇÚCAR', 'BOI']): return 'Agrícola 🚜'
    if 'TREASURIES' in nome: return 'Renda Fixa 🏛️'
    return 'Outros 🎲'

# 3. Paleta de Cores Consistente
CORES_SETOR = {
    'Criptoativos ₿': '#F7931A', 'Índices 📊': '#2962FF',
    'Metais ⛏️': '#FFD700', 'Energia ⚡': '#FF4500',
    'Moedas 💱': '#00C853', 'Agrícola 🚜': '#8D6E63',
    'Renda Fixa 🏛️': '#607D8B', 'Outros 🎲': '#9E9E9E'
}
CORES_SENTIMENTO = {"Otimista": "green", "Pessimista": "red"}

# ===============================
# 📥 ETL & PROCESSAMENTO
# ===============================

@st.cache_data
def load_data():
    if not os.path.exists("dados_dashboard.csv"):
        return pd.DataFrame()

    df = pd.read_csv("dados_dashboard.csv")
    df.columns = df.columns.str.strip()

    # Tipagem
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], errors="coerce")
    for col in ["Comprados", "Vendidos"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Feature Engineering
    df["Saldo_Liquido"] = df["Comprados"] - df["Vendidos"]
    df["Sentimento"] = df["Saldo_Liquido"].apply(lambda x: "Otimista" if x > 0 else "Pessimista")

    # Aplica Tradução e Classificação
    df["Ativo_Amigavel"] = df["nome_ativo"].apply(traduzir_nome_amigavel)
    df["Setor"] = df["Ativo_Amigavel"].apply(classificar_setor)

    # Extrai código original (Ticker)
    def extrair_codigo(texto):
        match = re.search(r"\((.*?)\)", str(texto))
        return match.group(1) if match else "N/A"
    df["Codigo"] = df["nome_ativo"].apply(extrair_codigo)
    
    return df.sort_values("data_referencia")

df_raw = load_data()

if df_raw.empty:
    st.error("❌ Base de dados vazia. Execute o ETL.")
    st.stop()

# ===============================
# 🧭 SIDEBAR
# ===============================

st.sidebar.title("🧠 Inteligência de Mercado")
pagina = st.sidebar.radio("Navegação:", ["🏢 Visão Macro (Setores)", "📈 Visão Micro (Ativo)", "🧪 Laboratório Quant"])

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Filtros")

# Filtro 1: Setor
setores = ["TODOS"] + sorted(df_raw["Setor"].unique())
setor_sel = st.sidebar.selectbox("Setor", setores)

if setor_sel != "TODOS":
    df = df_raw[df_raw["Setor"] == setor_sel]
else:
    df = df_raw.copy()

# Filtro 2: Ativo (Nome Amigável)
ativos = ["TODOS"] + sorted(df["Ativo_Amigavel"].unique())
ativo_sel = st.sidebar.selectbox("Ativo", ativos)

if ativo_sel != "TODOS":
    df = df[df["Ativo_Amigavel"] == ativo_sel]

# Filtro 3: Data
d_min, d_max = df["data_referencia"].min(), df["data_referencia"].max()
datas = st.sidebar.date_input("Período", [d_min, d_max])

if len(datas) == 2:
    df = df[(df["data_referencia"] >= pd.to_datetime(datas[0])) & (df["data_referencia"] <= pd.to_datetime(datas[1]))]

if df.empty:
    st.warning("⚠️ Sem dados para os filtros selecionados.")
    st.stop()

# ===============================
# 🏢 PÁGINA 1: MACRO (SETORES)
# ===============================
if pagina == "🏢 Visão Macro (Setores)":
    
    st.title(f"Panorama: {setor_sel}")
    
    data_recente = df["data_referencia"].max()
    df_last = df[df["data_referencia"] == data_recente].copy()

    # KPI Global do Setor
    if setor_sel != "TODOS":
        saldo = df_last["Saldo_Liquido"].sum()
        cor = "green" if saldo > 0 else "red"
        txt_vies = "COMPRADOR" if saldo > 0 else "VENDEDOR"
        st.markdown(f"### Viés Institucional: :{cor}[{txt_vies}]")
    
    st.divider()

    # Mapa de Calor (Treemap)
    st.subheader(f"Mapa de Fluxo de Dinheiro ({data_recente.strftime('%d/%m')})")
    df_last["Abs_Net"] = df_last["Saldo_Liquido"].abs()
    
    fig_map = px.treemap(
        df_last,
        path=[px.Constant(setor_sel), 'Ativo_Amigavel'],
        values='Abs_Net',
        color='Saldo_Liquido',
        color_continuous_scale=['red', 'gray', 'green'],
        color_continuous_midpoint=0,
        hover_data={'Saldo_Liquido': ':,.0f', 'Abs_Net': False},
        title="Tamanho = Volume | Cor = Direção (Verde=Compra, Vermelho=Venda)"
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Rankings
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🐂 Top Otimistas")
        st.dataframe(df_last.nlargest(5, "Saldo_Liquido")[["Ativo_Amigavel", "Saldo_Liquido"]].style.format({"Saldo_Liquido": "{:,.0f}"}).background_gradient(cmap="Greens"))
    with c2:
        st.subheader("🐻 Top Pessimistas")
        st.dataframe(df_last.nsmallest(5, "Saldo_Liquido")[["Ativo_Amigavel", "Saldo_Liquido"]].style.format({"Saldo_Liquido": "{:,.0f}"}).background_gradient(cmap="Reds_r"))

# ===============================
# 📈 PÁGINA 2: MICRO (ATIVO INTELIGENTE)
# ===============================
elif pagina == "📈 Visão Micro (Ativo)":
    
    if ativo_sel == "TODOS":
        ativo_foco = df["Ativo_Amigavel"].iloc[0]
        df_ativo = df[df["Ativo_Amigavel"] == ativo_foco]
        st.info(f"💡 Visualizando: **{ativo_foco}**. Para trocar, use o menu lateral.")
    else:
        df_ativo = df
        ativo_foco = ativo_sel

    ultimo = df_ativo.iloc[-1]
    
    st.title(f"{ativo_foco}")
    st.caption(f"Setor: {ultimo['Setor']} | Código: {ultimo['Codigo']}")

    # --- CÁLCULO DE INTELIGÊNCIA (Z-SCORE & DELTAS) ---
    media_hist = df_ativo["Saldo_Liquido"].mean()
    desvio_padrao = df_ativo["Saldo_Liquido"].std()
    
    # Define Status Estatístico (O quão fora da curva está o posicionamento?)
    status = "Neutro / Normal"
    if ultimo["Saldo_Liquido"] > (media_hist + 1.5 * desvio_padrao):
        status = "Extremamente Otimista (Sobrecomprado) ⚠️"
    elif ultimo["Saldo_Liquido"] < (media_hist - 1.5 * desvio_padrao):
        status = "Extremamente Pessimista (Sobrevendido) ⚠️"
        
    # Cálculo da Variação (Delta)
    if len(df_ativo) > 1:
        delta = ultimo['Saldo_Liquido'] - df_ativo.iloc[-2]['Saldo_Liquido']
    else:
        delta = 0

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Posição Líquida", f"{ultimo['Saldo_Liquido']:,.0f}".replace(",", "."), 
              delta=f"{delta:,.0f} (vs semana anterior)")
    
    c2.metric("Comprados / Vendidos", f"{ultimo['Comprados']:,.0f} / {ultimo['Vendidos']:,.0f}")
    c3.metric("Status Estatístico", status)

    # Gráfico de Tendência
    st.subheader("Tendência de Posicionamento")
    fig = px.line(df_ativo, x="data_referencia", y="Saldo_Liquido", markers=True)
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
    fig.add_hline(y=media_hist, line_dash="dot", line_color="yellow", annotation_text="Média Hist.")
    
    cor_linha = CORES_SETOR.get(ultimo["Setor"], "white")
    fig.update_traces(line_color=cor_linha, line_width=3)
    st.plotly_chart(fig, use_container_width=True)

    # Gráfico de Sazonalidade
    st.subheader("Padrão de Sazonalidade (Média Mensal)")
    df_ativo["Mês"] = df_ativo["data_referencia"].dt.month
    sazonal = df_ativo.groupby("Mês")["Saldo_Liquido"].mean().reset_index()
    
    fig_saz = px.bar(sazonal, x="Mês", y="Saldo_Liquido", 
                     color="Saldo_Liquido", color_continuous_scale=['red', 'gray', 'green'])
    fig_saz.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
    st.plotly_chart(fig_saz, use_container_width=True)

# ===============================
# 🧪 PÁGINA 3: QUANT
# ===============================
elif pagina == "🧪 Laboratório Quant":
    
    st.title("🔬 Correlação e Clusterização")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribuição (Histograma)")
        fig = px.histogram(df, x="Saldo_Liquido", color="Sentimento", color_discrete_map=CORES_SENTIMENTO)
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Quem está onde? (Scatter)")
        df["Tamanho"] = df["Saldo_Liquido"].abs()
        fig = px.scatter(
            df, x="Comprados", y="Vendidos", 
            color="Setor", size="Tamanho", 
            hover_name="Ativo_Amigavel", 
            color_discrete_map=CORES_SETOR,
            title="Clusterização por Setor"
        )
        st.plotly_chart(fig, use_container_width=True)