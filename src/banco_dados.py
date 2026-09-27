"""Persistência opcional do dataset em SQL Server via ambiente."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[1] / "dados_dashboard.csv"


def salvar_no_sql_server(data_path: Path = DEFAULT_DATA_PATH) -> None:
    """Substitui a tabela de destino com o dataset validado."""
    required = ["MSSQL_SERVER", "MSSQL_DATABASE", "MSSQL_USER", "MSSQL_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Configuração ausente: " + ", ".join(missing)
            + ". Configure o ambiente antes de executar."
        )

    driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")
    port = os.getenv("MSSQL_PORT", "1433")
    trust_certificate = os.getenv("MSSQL_TRUST_SERVER_CERTIFICATE", "yes")
    connection_string = (
        f"mssql+pyodbc://{quote_plus(os.environ['MSSQL_USER'])}:"
        f"{quote_plus(os.environ['MSSQL_PASSWORD'])}@"
        f"{os.environ['MSSQL_SERVER']}:{port}/{os.environ['MSSQL_DATABASE']}"
        f"?driver={quote_plus(driver)}"
        f"&TrustServerCertificate={trust_certificate}"
    )

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {path}")
    df = pd.read_csv(path)
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], errors="raise")
    engine = create_engine(connection_string)
    try:
        df.to_sql(name="TB_COT_REPORT", con=engine, if_exists="replace", index=False)
    finally:
        engine.dispose()
    print(f"Carga concluída: {len(df)} registros em TB_COT_REPORT")


if __name__ == "__main__":
    salvar_no_sql_server()
