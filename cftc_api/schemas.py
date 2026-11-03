from pydantic import BaseModel, ConfigDict, Field


class CotRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data_referencia: str
    nome_ativo: str
    comprados: int = Field(alias="Comprados")
    vendidos: int = Field(alias="Vendidos")


class AtivosResponse(BaseModel):
    ativos: list[str]


class HealthResponse(BaseModel):
    status: str
    records: int


class RootResponse(BaseModel):
    message: str
    docs: str
