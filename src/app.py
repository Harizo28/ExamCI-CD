"""
API FastAPI pour servir le modèle Breast Cancer.

Endpoints :
    GET  /         -> Health check + infos
    GET  /health   -> Health check simple (utilisé par Docker/Jenkins)
    POST /predict  -> Prédiction (0 = malin, 1 = bénin)
"""

import os
from typing import List

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------- Chargement du modèle ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "models", "model.pkl"))

# 30 features attendues par le modèle Breast Cancer
N_FEATURES = 30

app = FastAPI(
    title="Breast Cancer Prediction API",
    description="API MLOps servant un RandomForestClassifier via FastAPI.",
    version="1.0.0",
)

# Chargement paresseux : le modèle est chargé au démarrage si présent
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)


# ---------- Schémas Pydantic ----------
class PredictRequest(BaseModel):
    features: List[float] = Field(
        ...,
        description=f"Liste de {N_FEATURES} valeurs numériques (features Breast Cancer).",
        min_length=N_FEATURES,
        max_length=N_FEATURES,
    )


class PredictResponse(BaseModel):
    prediction: int
    label: str
    probability: float


# ---------- Endpoints ----------
@app.get("/")
def root():
    return {
        "message": "Breast Cancer Prediction API",
        "version": "1.0.0",
        "model_loaded": model is not None,
        "endpoints": ["/", "/health", "/predict"],
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Modèle non chargé. Vérifie que {MODEL_PATH} existe.",
        )

    X = np.array(payload.features).reshape(1, -1)
    pred = int(model.predict(X)[0])
    proba = float(model.predict_proba(X)[0][pred])

    return PredictResponse(
        prediction=pred,
        label="bénin" if pred == 1 else "malin",
        probability=round(proba, 4),
    )
