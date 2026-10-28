"""Persistência histórica do dataset CFTC em SQL Server."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import MetaData, Table, create_engine, delete, inspect

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[1] / "dados_dashboard.csv"
TABLE_NAME = "TB_COT_REPORT"
REQUIRED_COLUMNS = ["data_referencia", "nome_ativo", "Comprados", "Vendidos"]
KEY_COLUMNS = ["data_referencia", "nome_ativo"]


def _connection_string_from_environment() -> str:
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
    return (
        f"mssql+pyodbc://{quote_plus(os.environ['MSSQL_USER'])}:"
        f"{quote_plus(os.environ['MSSQL_PASSWORD'])}@"
        f"{os.environ['MSSQL_SERVER']}:{port}/{os.environ['MSSQL_DATABASE']}"
        f"?driver={quote_plus(driver)}"
        f"&TrustServerCertificate={trust_certificate}"
    )


def _validate_dataset(data: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(missing))
    if data.empty:
        raise ValueError("O dataset está vazio; a tabela histórica não foi alterada.")

    result = data[REQUIRED_COLUMNS].copy()
    result["data_referencia"] = pd.to_datetime(
        result["data_referencia"], errors="raise"
    )
    result["nome_ativo"] = result["nome_ativo"].astype("string").str.strip()
    result["Comprados"] = pd.to_numeric(result["Comprados"], errors="raise")
    result["Vendidos"] = pd.to_numeric(result["Vendidos"], errors="raise")

    if result[KEY_COLUMNS].isna().any().any() or result["nome_ativo"].eq("").any():
        raise ValueError("A chave data_referencia/nome_ativo não pode conter valores vazios")
    if result.duplicated(subset=KEY_COLUMNS).any():
        raise ValueError("O dataset contém chaves duplicadas (data_referencia, nome_ativo)")
    if result[["Comprados", "Vendidos"]].isna().any().any():
        raise ValueError("Comprados e Vendidos não podem conter valores vazios")

    return result


def salvar_no_sql_server(
    data_path: Path = DEFAULT_DATA_PATH,
    connection_url: str | None = None,
) -> None:
    """Atualiza as datas recebidas sem apagar períodos históricos anteriores.

    A chave lógica é (data_referencia, nome_ativo). O arquivo ETL é um snapshot
    completo dos períodos nele presentes: esses períodos são substituídos em uma
    única transação; datas fora do intervalo recebido permanecem na tabela.
    """
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {path}")

    data = _validate_dataset(pd.read_csv(path))
    database_url = connection_url or _connection_string_from_environment()
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            if inspect(connection).has_table(TABLE_NAME):
                table = Table(TABLE_NAME, MetaData(), autoload_with=connection)
                connection.execute(
                    delete(table).where(
                        table.c.data_referencia.between(
                            data["data_referencia"].min().to_pydatetime(),
                            data["data_referencia"].max().to_pydatetime(),
                        )
                    )
                )
            data.to_sql(
                name=TABLE_NAME,
                con=connection,
                if_exists="append",
                index=False,
            )
    finally:
        engine.dispose()

    print(
        f"Carga concluída: {len(data)} registros em {TABLE_NAME}; "
        f"período {data['data_referencia'].min().date()} a "
        f"{data['data_referencia'].max().date()}"
    )


if __name__ == "__main__":
    salvar_no_sql_server()
