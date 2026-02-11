import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuração da página
st.set_page_config(page_title='Analytic Suite - CFTC', layout='wide')

# -------------------------------
# CARREGAMENTO E TRATAMENTO
# -------------------------------

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "dados_dashboard.csv")

    if not os.path.exists(csv_path):
        st.error(f"Arquivo não encontrado em: {csv_path}")
        return pd.DataFrame()

    df = pd.read_csv(csv_path)

    # Tratamento de Tipos
    df['data_referencia'] = pd.to_datetime(df['data_referencia'], errors='coerce')
    df['Comprados'] = pd.to_numeric(df['Comprados'], errors='coerce').fillna(0).astype(int)
    df['Vendidos'] = pd.to_numeric(df['Vendidos'], errors='coerce').fillna(0).astype(int)

    # Feature Engineering
    df['Saldo_Liquido'] = df['Comprados'] - df['Vendidos']
    df['Sentimento'] = df['Saldo_Liquido'].apply(lambda x: 'Bullish' if x > 0 else 'Bearish')

    # Enriquecimento
    split_data = df['nome_ativo'].astype(str).str.rsplit(' - ', n=1, expand=True)

    if split_data.shape[1] > 1:
        df['Ativo_Limpo'] = split_data[0]
        df['Bolsa_Origem'] = split_data[1]
    else:
        df['Ativo_Limpo'] = df['nome_ativo']
        df['Bolsa_Origem'] = 'OUTROS'

    return df.sort_values(by='data_referencia')


df = load_data()

# -------------------------------
# SIDEBAR
# -------------------------------

st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.radio("Ir para:", ["📊 Dashboard Executivo", "🧪 Laboratório Estatístico"])

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros Globais")

if df.empty:
    st.error("Sem dados carregados.")
    st.stop()

# Filtro Bolsa
lista_bolsas = ['TODAS'] + sorted(df['Bolsa_Origem'].dropna().unique().tolist())
bolsa_selecionada = st.sidebar.selectbox('Filtrar por Bolsa (Exchange):', lista_bolsas)

if bolsa_selecionada != 'TODAS':
    df_filtered = df[df['Bolsa_Origem'] == bolsa_selecionada]
else:
    df_filtered = df

# Filtro Ativo
lista_ativos = sorted(df_filtered['Ativo_Limpo'].unique())
ativo_selecionado = st.sidebar.selectbox('Selecione o Ativo:', lista_ativos)

df_ativo = df_filtered[df_filtered['Ativo_Limpo'] == ativo_selecionado].sort_values(by='data_referencia')

# -------------------------------
# DASHBOARD EXECUTIVO
# -------------------------------

if pagina == "📊 Dashboard Executivo":
    st.title(f"📈 Monitoramento: {ativo_selecionado}")

    if not df_ativo.empty:
        ultimo = df_ativo.iloc[-1]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Data", ultimo['data_referencia'].strftime('%d/%m/%Y'))
        c2.metric("Posição Líquida", f"{ultimo['Saldo_Liquido']:,}")
        c3.metric("Comprados (Long)", f"{ultimo['Comprados']:,}")
        c4.metric("Vendidos (Short)", f"{ultimo['Vendidos']:,}")

        status_color = "green" if ultimo['Saldo_Liquido'] > 0 else "red"
        st.markdown(f"### :{status_color}[{ultimo['Sentimento']}]")

        st.subheader("Tendência de Saldo Líquido (Net Position)")

        fig_trend = px.line(
            df_ativo,
            x='data_referencia',
            y='Saldo_Liquido',
            markers=True
        )

        fig_trend.update_traces(line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)

# -------------------------------
# LABORATÓRIO ESTATÍSTICO
# -------------------------------

elif pagina == "🧪 Laboratório Estatístico":
    st.title(f"🔬 Análise Avançada: {ativo_selecionado}")

    if not df_ativo.empty:

        st.subheader("1. Estatística Descritiva")

        stats_df = df_ativo[['Comprados', 'Vendidos', 'Saldo_Liquido']].describe().T
        stats_df['Mediana'] = df_ativo[['Comprados', 'Vendidos', 'Saldo_Liquido']].median()
        stats_df['Moda'] = df_ativo[['Comprados', 'Vendidos', 'Saldo_Liquido']].mode().iloc[0]
        stats_df['Desvio Padrão'] = df_ativo[['Comprados', 'Vendidos', 'Saldo_Liquido']].std()

        st.dataframe(
            stats_df[['mean', 'Mediana', 'Moda', 'Desvio Padrão', 'min', 'max']]
            .style.format("{:.1f}")
        )

        col_esq, col_dir = st.columns(2)

        # Histograma
        with col_esq:
            st.subheader("2. Distribuição do Saldo")

            fig_hist = px.histogram(
                df_ativo,
                x="Saldo_Liquido",
                nbins=20
            )

            media_saldo = df_ativo['Saldo_Liquido'].mean()
            fig_hist.add_vline(
                x=media_saldo,
                line_dash="dash"
            )

            st.plotly_chart(fig_hist, use_container_width=True)

        # Scatter
        with col_dir:
            st.subheader("3. Correlação: Comprados vs Vendidos")

            df_plot = df_ativo.copy()
            df_plot['Tamanho_Absoluto'] = df_plot['Saldo_Liquido'].abs()

            fig_scatter = px.scatter(
                df_plot,
                x="Comprados",
                y="Vendidos",
                color="Sentimento",
                size="Tamanho_Absoluto",
                hover_data=['data_referencia', 'Saldo_Liquido']
            )

            st.plotly_chart(fig_scatter, use_container_width=True)
