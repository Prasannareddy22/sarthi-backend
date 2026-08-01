import importlib
import sys

import pytest
from fastapi.testclient import TestClient

ACCOUNT = {"name": "Hasini", "email": "hasini@example.com", "password": "secret123"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A TestClient backed by a throwaway SQLite file."""
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    for module in ("main", "crud", "auth", "db_models", "database"):
        sys.modules.pop(module, None)
    main = importlib.import_module("main")
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def profile_payload():
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


def test_register_stores_user_without_plaintext_password(client):
    response = client.post("/api/auth/register", json=ACCOUNT)
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "hasini@example.com"
    assert "password" not in body["user"] and "password_hash" not in body["user"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['token']}"})
    assert me.json()["user"]["name"] == "Hasini"


def test_duplicate_email_is_rejected(client):
    client.post("/api/auth/register", json=ACCOUNT)
    assert client.post("/api/auth/register", json=ACCOUNT).status_code == 409


def test_login_succeeds_and_rejects_wrong_password(client):
    client.post("/api/auth/register", json=ACCOUNT)

    ok = client.post("/api/auth/login", json={"email": ACCOUNT["email"], "password": "secret123"})
    assert ok.status_code == 200 and ok.json()["token"]

    bad = client.post("/api/auth/login", json={"email": ACCOUNT["email"], "password": "wrong123"})
    assert bad.status_code == 401


def test_submission_is_linked_to_the_signed_in_user(client, profile_payload):
    token = client.post("/api/auth/register", json=ACCOUNT).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/match-schemes", json=profile_payload, headers=headers)
    client.post("/api/match-schemes", json={**profile_payload, "name": "Anonymous"})

    mine = client.get("/api/my-profiles", headers=headers).json()
    assert [p["name"] for p in mine["profiles"]] == ["Lakshmi"]
    assert client.get("/api/profiles").json()["count"] == 2


def test_my_profiles_requires_a_token(client):
    assert client.get("/api/my-profiles").status_code == 401
