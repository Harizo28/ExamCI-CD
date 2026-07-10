"""
Tests pour le pipeline d'entraînement.
Exécutés par Jenkins au Stage 3 (avant l'entraînement réel).
"""

import os
import sys

# Ajoute src/ au PYTHONPATH pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from create_dataset import create_dataset  # noqa: E402


def test_dataset_creation(tmp_path):
    """Le dataset doit être créé, non vide, et contenir la colonne 'target'."""
    csv_file = tmp_path / "breast_cancer.csv"
    create_dataset(str(csv_file))

    assert csv_file.exists(), "Le CSV n'a pas été créé"

    import pandas as pd
    df = pd.read_csv(csv_file)

    assert len(df) > 0, "Le dataset est vide"
    assert "target" in df.columns, "La colonne 'target' est manquante"
    assert df.shape[1] == 31, f"Attendu 31 colonnes (30 features + target), reçu {df.shape[1]}"


def test_model_can_be_trained():
    """Vérifie qu'un RandomForest peut s'entraîner sur le dataset."""
    from sklearn.datasets import load_breast_cancer
    from sklearn.ensemble import RandomForestClassifier

    data = load_breast_cancer()
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(data.data, data.target)

    score = model.score(data.data, data.target)
    assert score > 0.9, f"Score trop bas : {score}"
