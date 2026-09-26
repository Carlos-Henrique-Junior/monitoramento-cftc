"""ETL seguro e reproduzível para os dados CFTC Financial Futures."""

from __future__ import annotations

import io
import os
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

URL_HISTORICO_2026 = "https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "dados_dashboard.csv"
REQUIRED_COLUMNS = ["data_referencia", "nome_ativo", "Comprados", "Vendidos"]


def extract_data(content: bytes) -> pd.DataFrame:
    """Extrai e valida o conteúdo ZIP retornado pela CFTC."""
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        members = [name for name in archive.namelist() if not name.endswith("/")]
        if not members:
            raise ValueError("O arquivo ZIP não contém dados")
        with archive.open(members[0]) as source:
            df = pd.read_csv(
                source,
                header=None,
                encoding="utf-8",
                usecols=[0, 1, 9, 10],
                names=["nome_ativo", "data_raw", "Comprados", "Vendidos"],
            )

    df["data_referencia"] = pd.to_datetime(
        df["data_raw"], format="%y%m%d", errors="coerce"
    )
    df["Comprados"] = pd.to_numeric(df["Comprados"], errors="coerce")
    df["Vendidos"] = pd.to_numeric(df["Vendidos"], errors="coerce")
    df["nome_ativo"] = df["nome_ativo"].astype("string").str.strip()
    df = df.dropna(subset=REQUIRED_COLUMNS)
    if df.empty:
        raise ValueError("Nenhum registro válido foi encontrado")
    if (df[["Comprados", "Vendidos"]] < 0).any().any():
        raise ValueError("Foram encontrados valores negativos nos campos de posição")

    result = df[REQUIRED_COLUMNS].sort_values("data_referencia").copy()
    result["Comprados"] = result["Comprados"].astype(int)
    result["Vendidos"] = result["Vendidos"].astype(int)
    return result


def save_atomic(df: pd.DataFrame, output_path: Path = OUTPUT_PATH) -> None:
    """Grava o resultado sem deixar um CSV parcialmente escrito."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", dir=output_path.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        df.to_csv(temporary, index=False)
    temporary_path.replace(output_path)


def run_etl(
    url: str | None = None,
    output_path: Path = OUTPUT_PATH,
    timeout: int = 30,
) -> pd.DataFrame:
    """Baixa, transforma, valida e persiste o dataset CFTC."""
    source_url = url or os.getenv("CFTC_SOURCE_URL", URL_HISTORICO_2026)
    response = requests.get(source_url, timeout=timeout)
    response.raise_for_status()
    result = extract_data(response.content)
    save_atomic(result, output_path)
    print(f"ETL concluído: {len(result)} registros em {output_path}")
    return result


if __name__ == "__main__":
    run_etl()
