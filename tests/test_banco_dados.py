import sys
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from banco_dados import salvar_no_sql_server


def test_persistencia_preserva_historico_e_atualiza_por_chave(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'cftc.db'}"

    def write_dataset(filename, rows):
        path = tmp_path / filename
        pd.DataFrame(rows).to_csv(path, index=False)
        return path

    historical = write_dataset(
        "historical.csv",
        [{
            "data_referencia": "2025-12-30",
            "nome_ativo": "EURO FX",
            "Comprados": 10,
            "Vendidos": 5,
        }],
    )
    current_year = write_dataset(
        "current.csv",
        [
            {
                "data_referencia": "2026-01-06",
                "nome_ativo": "EURO FX",
                "Comprados": 20,
                "Vendidos": 8,
            },
            {
                "data_referencia": "2026-01-13",
                "nome_ativo": "EURO FX",
                "Comprados": 22,
                "Vendidos": 9,
            },
        ],
    )
    correction = write_dataset(
        "correction.csv",
        [{
            "data_referencia": "2026-01-06",
            "nome_ativo": "EURO FX",
            "Comprados": 21,
            "Vendidos": 8,
        }],
    )

    salvar_no_sql_server(historical, connection_url=database_url)
    salvar_no_sql_server(current_year, connection_url=database_url)
    salvar_no_sql_server(current_year, connection_url=database_url)
    salvar_no_sql_server(correction, connection_url=database_url)

    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            result = pd.read_sql_query(
                text("SELECT data_referencia, nome_ativo, Comprados, Vendidos FROM TB_COT_REPORT"),
                connection,
            )
    finally:
        engine.dispose()

    assert len(result) == 3
    indexed = {
        (pd.to_datetime(row.data_referencia).date(), row.nome_ativo): row
        for row in result.itertuples(index=False)
    }
    assert indexed[(pd.Timestamp("2025-12-30").date(), "EURO FX")].Comprados == 10
    assert indexed[(pd.Timestamp("2026-01-06").date(), "EURO FX")].Comprados == 21
    assert indexed[(pd.Timestamp("2026-01-13").date(), "EURO FX")].Comprados == 22


def test_persistencia_rejeita_chaves_duplicadas(tmp_path):
    path = tmp_path / "duplicated.csv"
    pd.DataFrame(
        [
            {
                "data_referencia": "2026-01-06",
                "nome_ativo": "EURO FX",
                "Comprados": 20,
                "Vendidos": 8,
            },
            {
                "data_referencia": "2026-01-06",
                "nome_ativo": "EURO FX",
                "Comprados": 21,
                "Vendidos": 9,
            },
        ]
    ).to_csv(path, index=False)

    with pytest.raises(ValueError, match="chaves duplicadas"):
        salvar_no_sql_server(path, connection_url=f"sqlite:///{tmp_path / 'duplicates.db'}")
