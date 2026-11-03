"""Camada HTTP padronizada da API COT (CFTC)."""

from cftc_api.app import app, create_app

__all__ = ["app", "create_app"]
