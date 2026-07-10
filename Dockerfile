# =====================================================
#  Dockerfile — API FastAPI Breast Cancer
#  Base : python:3.11-slim (léger, stable, compatible sklearn)
# =====================================================
FROM python:3.11-slim

# ---------- Métadonnées ----------
LABEL maintainer="mlops-team"
LABEL description="API FastAPI servant un RandomForestClassifier"

# ---------- Variables d'environnement ----------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ---------- Répertoire de travail ----------
WORKDIR /app

# ---------- Dépendances système ----------
# curl est utilisé par le HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---------- Dépendances Python ----------
# Copier requirements en premier pour profiter du cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Code applicatif ----------
COPY src/ ./src/
COPY models/ ./models/

# ---------- Utilisateur non-root (sécurité) ----------
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ---------- Réseau ----------
EXPOSE 8000

# ---------- Healthcheck ----------
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ---------- Commande de démarrage ----------
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
