# 📊 Monitoramento de Mercado - COT Report (CFTC)

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Status](https://img.shields.io/badge/Status-Desenvolvimento-yellow?style=for-the-badge)]()

🔗 **Dashboard Online:**  
https://dashboard-mercado-cftc.streamlit.app  

---

## 📝 Sobre o Projeto

Projeto de Engenharia de Dados aplicado ao mercado financeiro, com foco na análise do relatório **Commitments of Traders (COT)**, publicado pela **CFTC (Commodity Futures Trading Commission)**.

A aplicação realiza a coleta automatizada dos dados oficiais, processa as posições de grandes participantes do mercado (Long vs Short) e disponibiliza as informações em um dashboard interativo para análise de sentimento.

---

## 🎯 Objetivo

Transformar dados brutos do COT em informações estruturadas e visualmente acessíveis, permitindo:

- Análise rápida de posicionamento institucional  
- Identificação de viés otimista ou pessimista  
- Acompanhamento histórico de posições compradas e vendidas  

---

## ⚙️ Arquitetura e Funcionalidades

### 🔹 Pipeline de Dados (ETL)

- Conexão automática com a fonte oficial da CFTC  
- Tratamento e padronização com Pandas  
- Consolidação da base histórica  
- Geração do arquivo `dados_dashboard.csv`  

Arquivo principal:
```
src/etl_pipeline.py
```

---

### 🔹 Dashboard Interativo

- Interface construída com Streamlit  
- Gráficos dinâmicos com Plotly  
- Filtros por ativo e período  
- Indicadores automáticos de posição líquida  

Arquivo principal:
```
src/dashboard.py
```

---

### 🔹 Automação

- Execução agendada via script `.bat` no Windows  
- Atualização recorrente da base de dados  
- Deploy contínuo no Streamlit Cloud  

---

## 🛠️ Tecnologias Utilizadas

**Linguagem**  
- Python 3.12+

**Bibliotecas**  
- Pandas  
- Requests  
- Streamlit  
- Plotly Express  

**Automação e Versionamento**  
- Git  
- Windows Task Scheduler  

**Cloud**  
- Streamlit Community Cloud  

---

## 🚀 Como Executar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/Carlos-Henrique-Junior/monitoramento-cftc.git
cd monitoramento-cftc
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute o pipeline de dados

```bash
python src/etl_pipeline.py
```

### 4. Inicie o dashboard

```bash
streamlit run src/dashboard.py
```

---

## 👨‍💻 Autor

**Carlos Henrique**  
LinkedIn: https://www.linkedin.com/in/carloshenrique-dados/  
GitHub: https://github.com/Carlos-Henrique-Junior  

---

Projeto desenvolvido como demonstração prática de pipeline de dados e visualização aplicada ao mercado financeiro.