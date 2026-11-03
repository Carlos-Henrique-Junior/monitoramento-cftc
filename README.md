# 📊 Monitoramento de Mercado - COT Report (CFTC)

**Python | Streamlit | Pandas | Data Analysis | Status: Em Desenvolvimento**

🔗 **Dashboard Online:**  
https://carlos-henrique-junior-monitoramento-cftc-srcdashboard-vkog1v.streamlit.app

---

# 📈 Market Intelligence Suite - COT Report (CFTC)

Monitoramento de Smart Money e Posicionamento Institucional

Este projeto é uma solução completa de Engenharia e Análise de Dados que extrai, processa e visualiza os dados do relatório **Commitments of Traders (COT)** da CFTC.

O objetivo é identificar tendências de mercado com base no posicionamento de grandes fundos e especuladores institucionais.

A aplicação implementa um pipeline estruturado com persistência histórica e análise estatística aplicada para suporte à tomada de decisão.

---

# 🏗️ Arquitetura da Solução

O projeto segue o fluxo:

**ETL → Data Warehouse → API → Analytics**

```mermaid
graph LR
    A["🌎 Fonte: CFTC.gov"] -->|"Extração & Tratamento (Python)"| B("⚙️ ETL Pipeline")
    B -->|Persistência| C[("🗄️ SQL Server / Docker")]
    C -->|Consulta| D{"🔌 API FastAPI"}
    D -->|Consumo| E["📊 Dashboard Streamlit"]
    C -->|Consumo| F["📈 Power BI / Excel"]
```

---

# 🚀 Funcionalidades

## 1️⃣ Engenharia de Dados (ETL)

### 🔹 Extração Automática  
Download do histórico anual direto da CFTC (arquivos ZIP).

### 🔹 Limpeza e Tratamento
- Ajuste de datas  
- Padronização de tipagem  
- Remoção de nulos  

### 🔹 Cálculo de Métricas
```
Net Position = Long - Short
```

### 🔹 Persistência
Armazenamento em SQL Server via Docker. A carga usa `(data_referencia, nome_ativo)` como chave lógica, rejeita chaves duplicadas no CSV e atualiza transacionalmente apenas o intervalo de datas recebido, preservando períodos históricos fora dele. Reprocessar o mesmo snapshot é idempotente.

O ETL padrão aponta para o arquivo CFTC de 2026. Para importar outro arquivo anual, configure `CFTC_SOURCE_URL` com a URL do ZIP antes de executar `src/etl_pipeline.py`; o ETL não baixa automaticamente todos os anos.

---

## 2️⃣ Dashboard Interativo (Streamlit)

- KPIs de tendência  
- Sentimento de mercado (Bullish / Bearish)  
- Evolução histórica  
- Média, Mediana, Desvio padrão e Correlação  
- Gráficos de linha  
- Histogramas  
- Scatter plots  
- Filtros por Ativo, Exchange e Data  

---

## 3️⃣ API Backend (FastAPI)

API de consulta somente leitura sobre o CSV gerado pelo ETL. A camada HTTP fica em `cftc_api/` (settings, schemas, routers e app factory); `src/api.py` é mantido como entrypoint compatível.

- `GET /` — status e link do Swagger
- `GET /health` — health check com o total de registros carregados
- `GET /ativos` — lista de ativos disponíveis
- `GET /dados/{ativo}?limit=100&offset=0` — histórico do ativo com paginação (máximo de 1000) e headers `X-Total-Count`, `X-Limit` e `X-Offset`
- Documentação automática em `/docs`

Rodar com `uvicorn src.api:app --reload` ou `uvicorn cftc_api.app:app --reload`. Testes da API: `pytest tests/test_api.py`.

A API não usa PostgreSQL nem JWT: a fonte é o CSV exportado pelo ETL e a consulta é pública e somente leitura. Migrar para banco e autenticação mudaria a arquitetura do projeto, então essa parte do padrão FastAPI não se aplica aqui.

---

# 🛠️ Tech Stack

- **Linguagem:** Python 3.12+  
- **Banco de Dados:** SQL Server (Docker)  
- **Backend:** FastAPI, Uvicorn  
- **Frontend:** Streamlit, Plotly  
- **Bibliotecas:** Pandas, SQLAlchemy, Requests, PyODBC  

---

# ⚙️ Como Executar o Projeto

## ✅ Pré-requisitos

- Python 3.x  
- Docker Desktop  
- Git  

---

## 1️⃣ Instalação

```bash
git clone https://github.com/Carlos-Henrique-Junior/monitoramento-cftc.git
cd monitoramento-cftc
pip install -r requirements.txt
```

---

## 2️⃣ Subindo o SQL Server (Docker)

```bash
docker run -e "ACCEPT_EULA=Y" \
-e "MSSQL_SA_PASSWORD=${MSSQL_SA_PASSWORD:?Set MSSQL_SA_PASSWORD in your local environment}" \
-p 1433:1433 \
-d mcr.microsoft.com/mssql/server:2022-latest
```

---

## 3️⃣ Executando o Pipeline

### ▶️ Rodar ETL

```bash
python src/etl_pipeline.py
python src/banco_dados.py
```

### ▶️ Iniciar Dashboard

```bash
streamlit run src/dashboard.py
```

### ▶️ (Opcional) Iniciar API

```bash
uvicorn src.api:app --reload
```

Documentação da API:

```
http://127.0.0.1:8000/docs
```

## EasyPanel dashboard container

The repository Dockerfile runs only the Streamlit dashboard on port `8501`, reading the checked-in `dados_dashboard.csv` snapshot. The SQL Server persistence/ETL and FastAPI endpoints are not started by this container; they require separate services and configuration. The dashboard snapshot is sourced from the public CFTC COT report.

---

# 📊 Estrutura do Projeto

```
📦 monitoramento-cftc
 ┣ 📂 src
 ┃ ┣ 📜 etl_pipeline.py
 ┃ ┣ 📜 dashboard.py
 ┃ ┣ 📜 banco_dados.py
 ┃ ┗ 📜 api.py
 ┣ 📂 cftc_api
 ┃ ┣ 📜 app.py
 ┃ ┣ 📜 settings.py
 ┃ ┣ 📜 data.py
 ┃ ┣ 📜 schemas.py
 ┃ ┗ 📂 routers
 ┃   ┗ 📜 cot.py
 ┣ 📂 tests
 ┃ ┣ 📜 test_api.py
 ┃ ┣ 📜 test_etl.py
 ┃ ┗ 📜 test_banco_dados.py
 ┣ 📜 dados_dashboard.csv
 ┣ 📜 requirements.txt
 ┣ 📜 requirements-dev.txt
 ┗ 📜 README.md
```

---

# 👨‍💻 Autor

**Carlos Henrique**

LinkedIn:  
https://www.linkedin.com/in/carlos-henrique-junior/

GitHub:  
https://github.com/Carlos-Henrique-Junior

Portfolio:
https://carlos-henrique-junior.github.io

Projeto desenvolvido como demonstração prática de pipeline de dados e visualização aplicada ao mercado financeiro.