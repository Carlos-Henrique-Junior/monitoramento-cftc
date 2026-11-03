"""Ponto de entrada compatível: uvicorn src.api:app --reload."""

from cftc_api.app import app, create_app

__all__ = ["app", "create_app"]
