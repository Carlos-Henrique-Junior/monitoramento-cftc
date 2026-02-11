import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuração da página (Layout Wide)
st.set_page_config(page_title='Analytic Suite - CFTC', layout='wide')

# --- CARREGAMENTO E ENRIQUECIMENTO DE DADOS ---
@st.cache_data
def load_data():
    if os.path.exists('dados_dashboard.csv'):
        df = pd.read_csv('dados_dashboard.csv')
        
        # Tratamento de Tipos
        df['data_referencia'] = pd.to_datetime(df['data_referencia'], errors='coerce')
        df['Comprados'] = pd.to_numeric(df['Comprados'], errors='coerce').fillna(0).astype(int)
        df['Vendidos'] = pd.to_numeric(df['Vendidos'], errors='coerce').fillna(0).astype(int)
        
        # Feature Engineering (Criação de Colunas)
        df['Saldo_Liquido'] = df['Comprados'] - df['Vendidos']
        df['Sentimento'] = df['Saldo_Liquido'].apply(lambda x: 'Bullish' if x > 0 else 'Bearish')
        
        # --- ENRIQUECIMENTO (Extração de Código/Texto) ---
        # Exemplo: "S&P 500 - CHICAGO MERCANTILE EXCHANGE" -> Extrair a Bolsa
        # Vamos dividir a string pelo traço " - "
        split_data = df['nome_ativo'].str.rsplit(' - ', n=1, expand=True)
        
        # Se a divisão funcionar, pega a parte 0 como Ativo e a 1 como Bolsa
        if split_data.shape[1] > 1:
            df['Ativo_Limpo'] = split_data[0]
            df['Bolsa_Origem'] = split_data[1]
        else:
            df['Ativo_Limpo'] = df['nome_ativo']
            df['Bolsa_Origem'] = 'OUTROS'
            
        return df.sort_values(by='data_referencia')
    return pd.DataFrame()

df = load_data()

# --- SIDEBAR (NAVEGAÇÃO E FILTROS) ---
st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.radio("Ir para:", ["📊 Dashboard Executivo", "🧪 Laboratório Estatístico"])

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros Globais")

if not df.empty:
    # Filtro 1: Bolsa (Enriquecido via tratamento de texto)
    lista_bolsas = ['TODAS'] + sorted(df['Bolsa_Origem'].dropna().unique().tolist())
    bolsa_selecionada = st.sidebar.selectbox('Filtrar por Bolsa (Exchange):', lista_bolsas)
    
    # Aplica filtro de Bolsa
    if bolsa_selecionada != 'TODAS':
        df_filtered = df[df['Bolsa_Origem'] == bolsa_selecionada]
    else:
        df_filtered = df

    # Filtro 2: Ativo
    lista_ativos = sorted(df_filtered['Ativo_Limpo'].unique())
    ativo_selecionado = st.sidebar.selectbox('Selecione o Ativo:', lista_ativos)
    
    # DataFrame Final do Ativo
    df_ativo = df[df['Ativo_Limpo'] == ativo_selecionado].sort_values(by='data_referencia')
else:
    st.error("Sem dados carregados.")
    st.stop()

# --- PÁGINA 1: DASHBOARD EXECUTIVO (O que já tínhamos) ---
if pagina == "📊 Dashboard Executivo":
    st.title(f"📈 Monitoramento: {ativo_selecionado}")
    st.caption(f"Bolsa de Origem: {df_ativo['Bolsa_Origem'].iloc[0] if not df_ativo.empty else 'N/A'}")
    
    if not df_ativo.empty:
        # Pega dado mais recente
        ultimo = df_ativo.iloc[-1]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Data", ultimo['data_referencia'].strftime('%d/%m/%Y'))
        c1.metric("Posição Líquida", f"{ultimo['Saldo_Liquido']:,}")
        c2.metric("Comprados (Long)", f"{ultimo['Comprados']:,}")
        c3.metric("Vendidos (Short)", f"{ultimo['Vendidos']:,}")
        
        status_color = "green" if ultimo['Saldo_Liquido'] > 0 else "red"
        c4.markdown(f"### :{status_color}[{ultimo['Sentimento']}]")
        
        # Gráfico de Tendência
        st.subheader("Tendência de Saldo Líquido (Net Position)")
        fig_trend = px.line(df_ativo, x='data_referencia', y='Saldo_Liquido', markers=True)
        fig_trend.update_traces(line_color='#3366CC', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)

# --- PÁGINA 2: LABORATÓRIO ESTATÍSTICO (NOVO!) ---
elif pagina == "🧪 Laboratório Estatístico":
    st.title(f"🔬 Análise Avançada: {ativo_selecionado}")
    
    if not df_ativo.empty:
        # 1. TABELA DE ESTATÍSTICA DESCRITIVA
        st.subheader("1. Estatística Descritiva (Ano 2026)")
        
        # Cálculo manual das métricas
        stats_df = df_ativo[['Comprados', 'Vendidos', 'Saldo_Liquido']].describe().T
        stats_df['Mediana'] = df_ativo[['Comprados', 'Vendidos', 'Saldo_Liquido']].median()
        stats_df['Moda'] = df_ativo[['Comprados', 'Vendidos', 'Saldo_Liquido']].mode().iloc[0]
        stats_df['Desvio Padrão'] = df_ativo[['Comprados', 'Vendidos', 'Saldo_Liquido']].std()
        
        st.dataframe(stats_df[['mean', 'Mediana', 'Moda', 'Desvio Padrão', 'min', 'max']].style.format("{:.1f}"))

        col_esq, col_dir = st.columns(2)

        # 2. HISTOGRAMA (Distribuição)
        with col_esq:
            st.subheader("2. Distribuição do Saldo (Histograma)")
            st.caption("Entenda a frequência dos posicionamentos. O mercado fica mais comprado ou vendido?")
            
            fig_hist = px.histogram(
                df_ativo, 
                x="Saldo_Liquido", 
                nbins=20, 
                title="Distribuição de Frequência",
                color_discrete_sequence=['#00CC96']
            )
            # Adiciona linha de média vertical
            media_saldo = df_ativo['Saldo_Liquido'].mean()
            fig_hist.add_vline(x=media_saldo, line_dash="dash", line_color="white", annotation_text="Média")
            st.plotly_chart(fig_hist, use_container_width=True)

        # 3. SCATTER PLOT (Correlação X vs Y)
        with col_dir:
            st.subheader("3. Correlação: Comprados vs Vendidos")
            st.caption("Existe relação entre o aumento de longs e shorts? (Dispersão)")
            
            # CRIAMOS UMA COLUNA TEMPORÁRIA COM VALOR ABSOLUTO PARA O TAMANHO
            df_ativo['Tamanho_Absoluto'] = df_ativo['Saldo_Liquido'].abs()

            fig_scatter = px.scatter(
                df_ativo, 
                x="Comprados", 
                y="Vendidos", 
                color="Sentimento",
                size="Tamanho_Absoluto", # Usamos o valor absoluto aqui (sempre positivo)
                hover_data=['data_referencia', 'Saldo_Liquido'], # Mostramos o saldo real no mouse
                title=f"Dispersão (Relação X vs Y)"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)