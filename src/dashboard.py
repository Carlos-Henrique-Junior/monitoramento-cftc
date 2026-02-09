import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title='Monitoramento CFTC', layout='wide')

@st.cache_data
def load_data():
    if os.path.exists('dados_dashboard.csv'):
        df = pd.read_csv('dados_dashboard.csv')
        # Converte a coluna de texto para Data real (Dia/Mês/Ano)
        df['data_referencia'] = pd.to_datetime(df['data_referencia'], errors='coerce')
        return df
    return pd.DataFrame()

st.title('📊 Monitoramento de Mercado (COT Report)')
st.markdown('**Desenvolvido por: Carlos Henrique**')
st.markdown('---')

df = load_data()

if not df.empty:
    st.sidebar.header('Filtros')

    # --- 1. FILTRO DE DATA ---
    # Pega as datas, remove duplicadas e ordena da mais recente para a antiga
    datas_disponiveis = df['data_referencia'].sort_values(ascending=False).unique()
    
    # Cria o seletor formatando a data para ficar bonita (Dia/Mês/Ano)
    data_selecionada = st.sidebar.selectbox(
        'Escolha a Data de Referência:',
        datas_disponiveis,
        format_func=lambda x: x.strftime('%d/%m/%Y')
    )

    # Filtra o DataFrame pela data escolhida
    df_filtrado_data = df[df['data_referencia'] == data_selecionada]

    # --- 2. FILTRO DE ATIVO ---
    # Mostra apenas os ativos disponíveis naquela data
    lista_ativos = sorted(df_filtrado_data['nome_ativo'].unique())
    ativo_selecionado = st.sidebar.selectbox('Escolha o Ativo:', lista_ativos)

    # Filtra pelo ativo final
    df_final = df_filtrado_data[df_filtrado_data['nome_ativo'] == ativo_selecionado]

    if not df_final.empty:
        # --- EXIBIÇÃO ---
        c1, c2, c3 = st.columns(3)
        long = int(df_final['Comprados'].iloc[0])
        short = int(df_final['Vendidos'].iloc[0])
        
        c1.metric('Comprados 🟢', f'{long:,}')
        c2.metric('Vendidos 🔴', f'{short:,}')
        
        sentimento = 'OTIMISTA 🚀' if long > short else 'PESSIMISTA 📉'
        c3.metric('Sentimento', sentimento)

        df_chart = df_final.melt(id_vars=['nome_ativo'], value_vars=['Comprados', 'Vendidos'], var_name='Tipo', value_name='Contratos')
        fig = px.bar(df_chart, x='Contratos', y='nome_ativo', color='Tipo', orientation='h', color_discrete_map={'Comprados': '#00C805', 'Vendidos': '#FF0000'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado encontrado para essa seleção.")
else:
    st.warning('⚠️ Arquivo dados_dashboard.csv não encontrado. Rode o etl_pipeline.py primeiro.')
