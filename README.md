# 📊 Monitoramento de Mercado - COT Report (CFTC)

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Status](https://img.shields.io/badge/Status-Concluído-success?style=for-the-badge)]()

> **Link do Dashboard Online:** [Acesse aqui](https://dashboard-mercado-cftc.streamlit.app)

## 📝 Sobre o Projeto

Este projeto é uma solução completa de **Engenharia de Dados** e **Business Intelligence** para monitoramento do mercado financeiro.

O sistema coleta automaticamente dados do relatório **Commitments of Traders (COT)** da CFTC (Commodity Futures Trading Commission), processa as informações sobre posições de grandes players (Comprados vs. Vendidos) e apresenta os dados em um dashboard interativo.

### 🎯 Objetivo
Facilitar a análise de sentimento do mercado (Otimista/Pessimista) para ativos futuros, permitindo uma visualização rápida do posicionamento institucional.

---

## ⚙️ Arquitetura e Funcionalidades

1.  **ETL (Extração, Transformação e Carga):**
    * Script Python (src/etl_pipeline.py) que conecta na fonte de dados da CFTC.
    * Limpeza e tratamento com **Pandas**.
    * Geração automática de base histórica (dados_dashboard.csv).

2.  **Visualização (Frontend):**
    * Dashboard interativo com **Streamlit**.
    * Gráficos dinâmicos com **Plotly**.
    * Filtros de Data e Ativos.
    * Indicadores de Sentimento automáticos (Long vs Short).

3.  **Automação e DevOps:**
    * Script Batch (.bat) para execução agendada no Windows.
    * Deploy contínuo (CI/CD) no **Streamlit Cloud**.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12+
* **Libs:** Pandas, Streamlit, Plotly Express, Requests
* **Automação:** Windows Batch Script, Git
* **Cloud:** Streamlit Community Cloud

---

## 🚀 Como Executar Localmente

1.  **Clone o repositório:**
    `ash
    git clone [https://github.com/Carlos-Henrique-Junior/monitoramento-cftc.git](https://github.com/Carlos-Henrique-Junior/monitoramento-cftc.git)
    `

2.  **Instale as dependências:**
    `ash
    pip install -r requirements.txt
    `

3.  **Execute o ETL (Baixar dados):**
    `ash
    python src/etl_pipeline.py
    `

4.  **Inicie o Dashboard:**
    `ash
    streamlit run src/dashboard.py
    `

---

## 👨‍💻 Autor

**Carlos Henrique**
* [LinkedIn](https://www.linkedin.com/in/carloshenrique-dados/) | [GitHub](https://github.com/Carlos-Henrique-Junior)

---
*Desenvolvido com 💙 e Python.*
