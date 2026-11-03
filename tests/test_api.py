import pandas as pd
import pytest
from fastapi.testclient import TestClient

from cftc_api.app import create_app
from cftc_api.settings import Settings


@pytest.fixture
def csv_path(tmp_path):
    path = tmp_path / "dados_dashboard.csv"
    pd.DataFrame(
        {
            "data_referencia": ["2026-02-03", "2026-02-10", "2026-02-03"],
            "nome_ativo": ["CL", "CL", "ES"],
            "Comprados": [8, 12, 4],
            "Vendidos": [2, 4, 1],
        }
    ).to_csv(path, index=False)
    return path


@pytest.fixture
def client(csv_path):
    app = create_app(Settings(data_path=csv_path))
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def empty_client(tmp_path):
    app = create_app(Settings(data_path=tmp_path / "ausente.csv"))
    with TestClient(app) as test_client:
        yield test_client


def test_root_aponta_para_docs(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_health_informa_total(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "records": 3}


def test_ativos_ordenados(client):
    response = client.get("/ativos")
    assert response.status_code == 200
    assert response.json() == {"ativos": ["CL", "ES"]}


def test_dados_filtra_case_insensitive_e_pagina(client):
    response = client.get("/dados/cl", params={"limit": 1, "offset": 1})
    assert response.status_code == 200
    assert response.headers["X-Total-Count"] == "2"
    body = response.json()
    assert len(body) == 1
    assert body[0]["nome_ativo"] == "CL"
    assert body[0]["Comprados"] == 12


def test_dados_de_ativo_inexistente_retorna_404(client):
    response = client.get("/dados/NAOEXISTE")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


def test_base_vazia_retorna_404(empty_client):
    assert empty_client.get("/ativos").status_code == 404
    assert empty_client.get("/dados/CL").status_code == 404
