"""
Entraîne un RandomForestClassifier sur Breast Cancer,
log les métriques + le modèle dans MLflow,
et sauvegarde le modèle en local (models/model.pkl).
"""

import os
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

# ---------- Chemins ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "breast_cancer.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

# ---------- MLflow ----------
# Si MLFLOW_TRACKING_URI est défini (dans Docker/Jenkins), on l'utilise,
# sinon fallback vers SQLite local (MLflow 2.17+ refuse le file store).
MLFLOW_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    f"sqlite:///{os.path.join(BASE_DIR, 'mlflow.db')}",
)
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "breast_cancer_rf")


def train():
    # 1. Chargement du dataset
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Dataset introuvable : {CSV_PATH}. "
            f"Lance d'abord : python src/create_dataset.py"
        )
    df = pd.read_csv(CSV_PATH)
    X = df.drop(columns=["target"])
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 2. Hyperparamètres (volontairement simples)
    params = {
        "n_estimators": 100,
        "max_depth": 5,
        "random_state": 42,
    }

    # 3. MLflow tracking
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run() as run:
        # Entraînement
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        # Prédictions + métriques
        y_pred = model.predict(X_test)
        metrics = {
            "accuracy":  accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall":    recall_score(y_test, y_pred),
            "f1_score":  f1_score(y_test, y_pred),
        }

        # Log dans MLflow
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, artifact_path="model")

        # Sauvegarde locale (utilisée par l'API FastAPI)
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(model, MODEL_PATH)

        # Log
        print(f"[MLflow] Tracking URI : {MLFLOW_URI}")
        print(f"[MLflow] Run ID       : {run.info.run_id}")
        print(f"[Metrics] {metrics}")
        print(f"[OK] Modèle sauvegardé : {MODEL_PATH}")

    return metrics


if __name__ == "__main__":
    train()
