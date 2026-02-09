import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuração da página
st.set_page_config(page_title='Monitoramento CFTC Pro', layout='wide')

# --- FUNÇÃO DE CARREGAMENTO E TRATAMENTO ---
@st.cache_data
def load_data():
    if os.path.exists('dados_dashboard.csv'):
        # Lê o arquivo
        df = pd.read_csv('dados_dashboard.csv')
        
        # Converte a coluna de data para o formato correto
        df['data_referencia'] = pd.to_datetime(df['data_referencia'], errors='coerce')
        
        # Garante que os números sejam inteiros
        df['Comprados'] = pd.to_numeric(df['Comprados'], errors='coerce').fillna(0).astype(int)
        df['Vendidos'] = pd.to_numeric(df['Vendidos'], errors='coerce').fillna(0).astype(int)
        
        # --- ENGENHARIA DE DADOS ---
        # 1. Saldo Líquido (Net Position)
        df['Saldo_Liquido'] = df['Comprados'] - df['Vendidos']
        
        # 2. Definição do Sentimento
        df['Sentimento'] = df['Saldo_Liquido'].apply(lambda x: 'Bullish (Otimista)' if x > 0 else 'Bearish (Pessimista)')
        
        return df.sort_values(by='data_referencia')
    return pd.DataFrame()

# --- INTERFACE PRINCIPAL ---
st.title('📈 Intelligence Dashboard - COT Report')
st.info("ℹ️ **Nota:** Os dados do COT são divulgados pela CFTC sempre às sextas-feiras, referentes à terça-feira anterior.")
st.markdown('---')

df = load_data()

if not df.empty:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header('🔍 Filtros de Análise')
    
    # 1. Filtro de Ativo
    lista_ativos = sorted(df['nome_ativo'].unique())
    ativo_selecionado = st.sidebar.selectbox('Selecione o Ativo:', lista_ativos)
    
    # Filtra o dataframe pelo ativo (Histórico completo deste ativo)
    df_ativo_full = df[df['nome_ativo'] == ativo_selecionado].sort_values(by='data_referencia')
    
    # 2. Filtro de Data (VOLTOU! 🔙)
    # Pega as datas disponíveis para esse ativo, da mais recente para a mais antiga
    datas_disponiveis = df_ativo_full['data_referencia'].sort_values(ascending=False).unique()
    
    data_selecionada = st.sidebar.selectbox(
        'Escolha a Data de Referência:',
        datas_disponiveis,
        format_func=lambda x: x.strftime('%d/%m/%Y')
    )
    
    # --- LÓGICA DE FILTRAGEM ---
    # Encontra a linha exata da data selecionada
    dados_selecionados = df_ativo_full[df_ativo_full['data_referencia'] == data_selecionada]

    if not dados_selecionados.empty:
        # Pega os dados da data escolhida
        dado_atual = dados_selecionados.iloc[0]
        
        # Tenta pegar a semana anterior (comparado à data selecionada) para o Delta
        # Acha o índice da data atual e tenta pegar o anterior
        idx_atual = df_ativo_full[df_ativo_full['data_referencia'] == data_selecionada].index[0]
        # Pega o histórico até essa data para achar o anterior
        historico_anterior = df_ativo_full[df_ativo_full['data_referencia'] < data_selecionada]
        
        if not historico_anterior.empty:
            dado_anterior = historico_anterior.iloc[-1]
            delta_net = int(dado_atual['Saldo_Liquido'] - dado_anterior['Saldo_Liquido'])
        else:
            delta_net = 0

        # --- KPI CARDS (Baseados na DATA SELECIONADA) ---
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.metric("📅 Data Analisada", dado_atual['data_referencia'].strftime('%d/%m/%Y'))
        with c2:
            st.metric("💰 Posição Líquida (Net)", f"{int(dado_atual['Saldo_Liquido']):,}", delta=f"{delta_net:,} contratos")
        with c3:
            st.metric("🟢 Comprados (Long)", f"{int(dado_atual['Comprados']):,}")
        with c4:
            cor_texto = "green" if dado_atual['Saldo_Liquido'] > 0 else "red"
            st.markdown(f"**Sentimento na Data:**")
            st.markdown(f":{cor_texto}[**{dado_atual['Sentimento']}**]")

        # --- GRÁFICO 1: EVOLUÇÃO HISTÓRICA ---
        st.markdown('### ⏳ Tendência (Histórico Completo)')
        
        fig_evolucao = go.Figure()
        
        # Linha de tendência
        fig_evolucao.add_trace(go.Scatter(
            x=df_ativo_full['data_referencia'], 
            y=df_ativo_full['Saldo_Liquido'],
            mode='lines',
            name='Saldo Líquido',
            line=dict(color='#3366CC', width=3)
        ))
        
        # Bolinha marcando a data selecionada
        fig_evolucao.add_trace(go.Scatter(
            x=[dado_atual['data_referencia']],
            y=[dado_atual['Saldo_Liquido']],
            mode='markers',
            name='Data Selecionada',
            marker=dict(color='red', size=12, symbol='circle-open-dot')
        ))
        
        fig_evolucao.update_layout(
            title=f'Linha do Tempo: {ativo_selecionado}',
            xaxis_title='Data',
            yaxis_title='Saldo de Contratos',
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)

        # --- GRÁFICO 2: BARRA (DA DATA SELECIONADA) ---
        st.markdown('### ⚔️ Batalha: Comprados vs Vendidos (Nesta Data)')
        
        # Prepara dataframe só para o gráfico de barras
        df_chart = pd.DataFrame([
            {'Tipo': 'Comprados', 'Contratos': dado_atual['Comprados']},
            {'Tipo': 'Vendidos', 'Contratos': dado_atual['Vendidos']}
        ])
        
        fig_comp = px.bar(
            df_chart, 
            x='Contratos', 
            y='Tipo',
            orientation='h',
            color='Tipo',
            color_discrete_map={'Comprados': '#00C805', 'Vendidos': '#FF0000'},
            text='Contratos'
        )
        fig_comp.update_layout(template='plotly_dark', height=300)
        st.plotly_chart(fig_comp, use_container_width=True)

        # --- TABELA DE DADOS ---
        with st.expander("📂 Ver Histórico Completo em Tabela"):
            st.dataframe(
                df_ativo_full[['data_referencia', 'nome_ativo', 'Comprados', 'Vendidos', 'Saldo_Liquido', 'Sentimento']]
                .sort_values(by='data_referencia', ascending=False)
                .style.format({'Comprados': '{:,}', 'Vendidos': '{:,}', 'Saldo_Liquido': '{:,}'})
            )
            
    else:
        st.warning("⚠️ Dados não encontrados para esta data.")

else:
    st.error("⚠️ Arquivo de dados não encontrado. Rode o ETL primeiro.")