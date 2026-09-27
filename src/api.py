"""API REST para consulta dos dados de posicionamento COT (CFTC)."""

from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

DATA_PATH = Path(__file__).resolve().parents[1] / "dados_dashboard.csv"

app = FastAPI(
    title="API COT Report",
    description="API para consulta de dados de posicionamento de mercado (CFTC)",
    version="1.0"
)

# Carrega os dados na memória ao iniciar
def get_data() -> pd.DataFrame:
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
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
    # Filtra pelo nome (contém o texto literal, case insensitive)
    df_filtrado = df[df['nome_ativo'].str.contains(ativo, case=False, na=False, regex=False)]

    if df_filtrado.empty:
        raise HTTPException(status_code=404, detail=f"Ativo '{ativo}' não encontrado")

    # Converte para dicionário (JSON)
    return df_filtrado.to_dict(orient="records")

# Para rodar: uvicorn src.api:app --reload
