from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cftc_api.data import CotStore
from cftc_api.routers import cot
from cftc_api.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.store = CotStore(resolved.data_path)
        yield

    application = FastAPI(
        title="API COT Report",
        description=("API para consulta de dados de posicionamento de mercado (CFTC)"),
        version="1.0",
        lifespan=lifespan,
    )
    application.include_router(cot.router, tags=["COT"])
    return application


app = create_app()
