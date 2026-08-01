import importlib
import sys

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A TestClient backed by a throwaway SQLite file."""
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    for module in ("main", "crud", "db_models", "database"):
        sys.modules.pop(module, None)
    main = importlib.import_module("main")
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def payload():
    return {
        "name": "Lakshmi",
        "gender": "Female",
        "is_income_tax_payer": False,
        "is_government_employee": False,
        "is_head_of_family": True,
        "annual_income": 100000,
        "has_lpg_connection": True,
        "is_permanent_resident": True,
        "has_white_ration_card": True,
        "age": 30,
        "is_rural": True,
        "caste": "BC",
        "religion": "Hindu",
        "electricity_consumption": 150,
        "has_electricity_bill_dues": False,
    }


def test_match_schemes_persists_profile(client, payload):
    response = client.post("/api/match-schemes", json=payload)
    assert response.status_code == 200
    profile_id = response.json()["profile_id"]

    stored = client.get(f"/api/profiles/{profile_id}").json()["profile"]
    assert stored["name"] == "Lakshmi"
    assert stored["caste_group"] == "BC"
    assert len(stored["details"]) == len(response.json()["details"])


def test_list_profiles_returns_newest_first(client, payload):
    client.post("/api/match-schemes", json=payload)
    client.post("/api/match-schemes", json={**payload, "name": "Ravi", "gender": "Male"})

    profiles = client.get("/api/profiles").json()["profiles"]
    assert [p["name"] for p in profiles] == ["Ravi", "Lakshmi"]


def test_unknown_profile_returns_404(client):
    assert client.get("/api/profiles/9999").status_code == 404
