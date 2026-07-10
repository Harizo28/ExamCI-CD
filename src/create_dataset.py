"""
Génère le dataset Breast Cancer au format CSV.
Exécuté une seule fois avant le premier entraînement.
"""

import os
import pandas as pd
from sklearn.datasets import load_breast_cancer

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "breast_cancer.csv")


def create_dataset(output_path: str = CSV_PATH) -> str:
    """Charge le dataset scikit-learn et l'écrit en CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = load_breast_cancer(as_frame=True)
    df: pd.DataFrame = data.frame  # features + target
    df.to_csv(output_path, index=False)

    print(f"[OK] Dataset créé : {output_path}")
    print(f"[INFO] Shape : {df.shape}")
    return output_path


if __name__ == "__main__":
    create_dataset()
