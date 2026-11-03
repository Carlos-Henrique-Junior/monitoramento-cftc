from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["data_referencia", "nome_ativo", "Comprados", "Vendidos"]


class CotStore:
    """Mantém o CSV carregado em memória durante o ciclo de vida da aplicação."""

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self._data = self._load(data_path)

    @staticmethod
    def _load(data_path: Path) -> pd.DataFrame:
        if not data_path.exists():
            return pd.DataFrame(columns=REQUIRED_COLUMNS)

        data = pd.read_csv(data_path)
        missing = [column for column in REQUIRED_COLUMNS if column not in data]
        if missing:
            raise ValueError(f"CSV sem colunas obrigatórias: {', '.join(missing)}")
        data["data_referencia"] = data["data_referencia"].astype(str)
        data["nome_ativo"] = data["nome_ativo"].astype(str)
        data["Comprados"] = data["Comprados"].astype(int)
        data["Vendidos"] = data["Vendidos"].astype(int)
        return data

    @property
    def is_empty(self) -> bool:
        return self._data.empty

    @property
    def total(self) -> int:
        return len(self._data)

    def ativos(self) -> list[str]:
        return sorted(self._data["nome_ativo"].unique().tolist())

    def filtrar_por_ativo(self, termo: str) -> pd.DataFrame:
        return self._data[
            self._data["nome_ativo"].str.contains(
                termo, case=False, na=False, regex=False
            )
        ]
