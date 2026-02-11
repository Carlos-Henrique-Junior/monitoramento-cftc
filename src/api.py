from fastapi import FastAPI, HTTPException
import pandas as pd
import os

app = FastAPI(
    title="API COT Report",
    description="API para consulta de dados de posicionamento de mercado (CFTC)",
    version="1.0"
)

# Carrega os dados na memória ao iniciar
def get_data():
    if os.path.exists('dados_dashboard.csv'):
        return pd.read_csv('dados_dashboard.csv')
    return pd.DataFrame()

@app.get("/")
def home():
    return {"message": "API COT Report Online 🚀", "docs": "/docs"}

@app.get("/ativos")
def listar_ativos():
    """Retorna a lista de todos os ativos disponíveis."""
    df = get_data()
    if df.empty:
        raise HTTPException(status_code=404, detail="Base de dados vazia")
    return {"ativos": df['nome_ativo'].unique().tolist()}

@app.get("/dados/{ativo}")
def pegar_dados_ativo(ativo: str):
    """Retorna o histórico completo de um ativo específico."""
    df = get_data()
    # Filtra pelo nome (contém o texto, case insensitive)
    df_filtrado = df[df['nome_ativo'].str.contains(ativo, case=False, na=False)]
    
    if df_filtrado.empty:
        raise HTTPException(status_code=404, detail=f"Ativo '{ativo}' não encontrado")
    
    # Converte para dicionário (JSON)
    return df_filtrado.to_dict(orient="records")

# Para rodar: uvicorn src.api:app --reload