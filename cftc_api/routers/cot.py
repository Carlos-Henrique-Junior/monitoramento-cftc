from typing import Annotated

import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Request, Response, status

from cftc_api.data import CotStore
from cftc_api.schemas import (
    AtivosResponse,
    CotRecord,
    HealthResponse,
    RootResponse,
)

router = APIRouter()


def get_store(request: Request) -> CotStore:
    return request.app.state.store


@router.get("/", response_model=RootResponse, summary="Status da API")
def home() -> RootResponse:
    return RootResponse(message="API COT Report Online 🚀", docs="/docs")


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health(request: Request) -> HealthResponse:
    store = get_store(request)
    return HealthResponse(status="ok", records=store.total)


@router.get(
    "/ativos",
    response_model=AtivosResponse,
    summary="Lista os ativos disponíveis",
)
def listar_ativos(request: Request) -> AtivosResponse:
    store = get_store(request)
    if store.is_empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base de dados vazia",
        )
    return AtivosResponse(ativos=store.ativos())


@router.get(
    "/dados/{ativo}",
    response_model=list[CotRecord],
    summary="Histórico de um ativo",
)
def pegar_dados_ativo(
    ativo: str,
    request: Request,
    response: Response,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict]:
    store = get_store(request)
    if store.is_empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base de dados vazia",
        )

    encontrados: pd.DataFrame = store.filtrar_por_ativo(ativo)
    if encontrados.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ativo '{ativo}' não encontrado",
        )

    response.headers["X-Total-Count"] = str(len(encontrados))
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Offset"] = str(offset)
    pagina = encontrados.iloc[offset : offset + limit]
    return pagina.to_dict(orient="records")
