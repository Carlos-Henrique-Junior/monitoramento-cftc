import io
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from etl_pipeline import extract_data, save_atomic


def make_zip() -> bytes:
    rows = [
        "ES,260210,0,0,0,0,0,0,0,12,4",
        "CL,260203,0,0,0,0,0,0,0,8,2",
    ]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("sample.txt", "\n".join(rows))
    return buffer.getvalue()


def test_extract_data_normalizes_and_sorts_records():
    result = extract_data(make_zip())
    assert list(result.columns) == [
        "data_referencia", "nome_ativo", "Comprados", "Vendidos"
    ]
    assert result.iloc[0]["nome_ativo"] == "CL"
    assert result["Comprados"].tolist() == [8, 12]
    assert result["Vendidos"].tolist() == [2, 4]


def test_save_atomic_writes_valid_csv(tmp_path):
    result = extract_data(make_zip())
    destination = tmp_path / "nested" / "dados.csv"
    save_atomic(result, destination)
    loaded = pd.read_csv(destination)
    assert len(loaded) == 2
    assert loaded["nome_ativo"].tolist() == ["CL", "ES"]
