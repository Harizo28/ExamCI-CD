"""
Tests pour l'API FastAPI.
Utilise TestClient (basé sur httpx) : ne démarre pas de vrai serveur.
"""

import os
import sys

import joblib
import pytest
from fastapi.testclient import TestClient
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier

# Ajoute src/ au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """Crée un modèle jouet, le sauvegarde, puis instancie l'API."""
    # 1. Entraîner un mini modèle et le sauvegarder dans un tmp
    tmp_dir = tmp_path_factory.mktemp("models")
    model_path = tmp_dir / "model.pkl"

    data = load_breast_cancer()
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(data.data, data.target)
    joblib.dump(model, str(model_path))

    # 2. Pointer l'API vers ce modèle AVANT d'importer app
    os.environ["MODEL_PATH"] = str(model_path)

    # 3. Réimporter proprement app pour prendre en compte le MODEL_PATH
    import importlib
    import app as app_module
    importlib.reload(app_module)

    return TestClient(app_module.app)


def test_root(client):
    """GET / doit retourner 200 + les infos de base."""
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Breast Cancer Prediction API"
    assert data["model_loaded"] is True


def test_health(client):
    """GET /health doit retourner status=ok."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_valid(client):
    """POST /predict avec 30 features doit renvoyer une prédiction 0 ou 1."""
    data = load_breast_cancer()
    sample = data.data[0].tolist()  # premier échantillon

    r = client.post("/predict", json={"features": sample})
    assert r.status_code == 200

    body = r.json()
    assert body["prediction"] in [0, 1]
    assert body["label"] in ["malin", "bénin"]
    assert 0.0 <= body["probability"] <= 1.0


def test_predict_invalid_length(client):
    """POST /predict avec le mauvais nombre de features doit renvoyer 422."""
    r = client.post("/predict", json={"features": [1.0, 2.0, 3.0]})
    assert r.status_code == 422  # Pydantic validation error
