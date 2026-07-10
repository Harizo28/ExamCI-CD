# 🧬 MLOps Breast Cancer — Pipeline CI/CD complet

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![MLflow](https://img.shields.io/badge/MLflow-2.17-0194E2.svg)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-LTS-D24939.svg)](https://www.jenkins.io/)

> **Projet pédagogique MLOps** démontrant un pipeline CI/CD complet de bout en bout : de l'entraînement d'un modèle Scikit-Learn jusqu'à son déploiement automatique via une API FastAPI, orchestré par Jenkins.

---

## 📋 Table des matières

- [🎯 Objectifs](#-objectifs)
- [🏗️ Architecture](#️-architecture)
- [📂 Structure du projet](#-structure-du-projet)
- [🚀 Démarrage rapide](#-démarrage-rapide)
- [🧪 Tests](#-tests)
- [🔄 Pipeline CI/CD](#-pipeline-cicd)
- [📊 Services & Endpoints](#-services--endpoints)
- [🛠️ Stack technique](#️-stack-technique)
- [❓ Troubleshooting](#-troubleshooting)
- [📚 Documentation](#-documentation)

---

## 🎯 Objectifs

Ce projet a pour but pédagogique de mettre en pratique une **chaîne MLOps professionnelle** :

- ✅ Versionner code + config avec **Git/GitHub**
- ✅ Entraîner un modèle **Scikit-Learn** simple (RandomForest sur Breast Cancer)
- ✅ Tracker les expériences avec **MLflow** + **PostgreSQL**
- ✅ Servir le modèle via une **API FastAPI**
- ✅ Conteneuriser l'ensemble avec **Docker** & **Docker Compose**
- ✅ Automatiser tests / build / déploiement avec **Jenkins**

> ⚠️ **Note** : le modèle ML est volontairement simple. L'accent est mis sur la **chaîne CI/CD**, pas sur la performance ML.

---

## 🏗️ Architecture

```
┌─────────────┐  git push   ┌──────────┐   poll SCM   ┌─────────────────────┐
│   Dev       │────────────▶│  GitHub  │◀─────────────│    Jenkins          │
└─────────────┘             └──────────┘              │  (Docker container) │
                                                      └──────────┬──────────┘
                                                                 │ exécute
                                                                 ▼
                                          ┌────────────────────────────────────────┐
                                          │  Pipeline (Jenkinsfile) — 7 stages     │
                                          │  1. Checkout        5. Verify MLflow   │
                                          │  2. Install deps    6. Docker build    │
                                          │  3. Run tests       7. Deploy          │
                                          │  4. Train model                        │
                                          └──────────────┬─────────────────────────┘
                                                         │ déploie
                                                         ▼
                    ┌────────────────────────────────────────────────────────┐
                    │                docker-compose network                  │
                    │  ┌──────────┐    ┌──────────┐    ┌──────────────┐      │
                    │  │ postgres │◀───│  mlflow  │    │  api         │      │
                    │  │  :5432   │    │  :5000   │    │  (FastAPI)   │      │
                    │  └──────────┘    └──────────┘    │  :8000       │      │
                    │                                  └──────────────┘      │
                    └────────────────────────────────────────────────────────┘
```

---

## 📂 Structure du projet

```
mlops-breast-cancer/
├── .dockerignore
├── .env.example                    # Template variables d'env
├── .gitignore
├── docker-compose.yml              # Stack : postgres + mlflow + api
├── Dockerfile                      # Image de l'API FastAPI
├── Jenkinsfile                     # Pipeline CI/CD (7 stages)
├── README.md
├── requirements.txt                # Dépendances Python
│
├── data/
│   └── breast_cancer.csv           # Dataset (généré par script)
├── models/
│   └── model.pkl                   # Modèle entraîné (généré)
│
├── src/
│   ├── create_dataset.py           # Génère data/breast_cancer.csv
│   ├── train.py                    # Entraîne + log MLflow
│   └── app.py                      # API FastAPI
│
├── tests/
│   ├── test_train.py               # Tests d'entraînement
│   └── test_api.py                 # Tests de l'API
│
├── jenkins/
│   ├── Dockerfile.jenkins          # Jenkins + Docker CLI + Python
│   └── docker-compose.jenkins.yml  # Lance Jenkins
│
└── docs/
    └── git-cheatsheet.md           # Aide-mémoire Git
```

---

## 🚀 Démarrage rapide

### Prérequis

- **Docker Desktop** (Windows/Mac) ou **Docker Engine + Compose** (Linux)
- **Python 3.11+** (pour développement local, facultatif)
- **Git**
- **Compte GitHub** + Personal Access Token (PAT)

### 1. Cloner le projet

```bash
git clone https://github.com/TON_USER/mlops-breast-cancer.git
cd mlops-breast-cancer
```

### 2. Configuration

```bash
cp .env.example .env
# Édite .env si besoin
```

### 3. Lancer la stack MLOps

```bash
# Générer le modèle initial (local ou via docker)
python -m venv .venv
source .venv/bin/activate            # Windows : .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/create_dataset.py
python src/train.py

# Lancer tous les services
docker compose up -d --build
docker compose ps
```

Services accessibles :

| Service | URL |
|---------|-----|
| API FastAPI | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| MLflow UI | http://localhost:5000 |
| PostgreSQL | `localhost:5432` (user: `mlflow` / pass: `mlflowpass`) |

### 4. Lancer Jenkins

```bash
cd jenkins
docker compose -f docker-compose.jenkins.yml up -d --build
```

- Ouvrir http://localhost:8080
- Récupérer le mot de passe admin :
  ```bash
  docker exec mlops_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  ```
- Suivre le setup (voir [docs/git-cheatsheet.md](docs/git-cheatsheet.md) et le guide Jenkins)
- Créer un job **Pipeline** connecté à ce dépôt GitHub

### 5. Tester l'API

```bash
# Health check
curl http://localhost:8000/health

# Prédiction (30 features)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[14.0,20.0,90.0,600.0,0.1,0.1,0.1,0.05,0.2,0.06,
                   0.5,1.0,3.0,40.0,0.005,0.02,0.02,0.01,0.02,0.003,
                   16.0,25.0,105.0,800.0,0.13,0.25,0.28,0.11,0.3,0.08]}'
```

Réponse attendue :

```json
{
  "prediction": 1,
  "label": "bénin",
  "probability": 0.94
}
```

---

## 🧪 Tests

```bash
# Tous les tests
pytest tests/ -v

# Un seul fichier
pytest tests/test_api.py -v

# Avec rapport JUnit (utilisé par Jenkins)
pytest tests/ --junitxml=reports/junit.xml
```

6 tests couvrent :

- ✅ Création du dataset
- ✅ Entraînement du modèle
- ✅ Endpoint `GET /`
- ✅ Endpoint `GET /health`
- ✅ Endpoint `POST /predict` (payload valide)
- ✅ Endpoint `POST /predict` (payload invalide → 422)

---

## 🔄 Pipeline CI/CD

Le fichier [`Jenkinsfile`](Jenkinsfile) définit un pipeline en **7 stages** :

| # | Stage | Rôle |
|---|-------|------|
| 1 | **Checkout** | Clone la dernière version du code depuis GitHub |
| 2 | **Install dependencies** | Crée un venv + `pip install -r requirements.txt` |
| 3 | **Run tests** | Exécute `pytest` + publie le rapport JUnit |
| 4 | **Train model** | Génère le dataset + entraîne le modèle + archive `model.pkl` |
| 5 | **Verify MLflow** | Vérifie que le run a bien été loggué dans MLflow/PostgreSQL |
| 6 | **Build Docker image** | Build `mlops-breast-cancer-api:${BUILD_NUMBER}` |
| 7 | **Deploy** | `docker compose up -d --force-recreate api` + healthcheck |

### Déclenchement

- **Manuel** : bouton *Build Now* dans Jenkins
- **Automatique** : Poll SCM toutes les 5 min (`H/5 * * * *`)
- **Webhook** : à chaque `git push` (si Jenkins est accessible depuis Internet)

### Visualisation

Le plugin **Blue Ocean** offre une vue graphique moderne du pipeline :
`Dashboard → Open Blue Ocean`

---

## 📊 Services & Endpoints

### API FastAPI (port 8000)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Infos générales + statut du modèle |
| `GET` | `/health` | Healthcheck (utilisé par Docker/Jenkins) |
| `POST` | `/predict` | Prédiction (30 features → 0/1) |
| `GET` | `/docs` | Swagger UI interactif |

### MLflow (port 5000)

- Interface web pour visualiser les expériences, runs, métriques
- Backend store : **PostgreSQL**
- Artifact store : volume Docker `mlflow_artifacts`

### PostgreSQL (port 5432)

- Base : `mlflow`
- User / password : `mlflow` / `mlflowpass` (à changer en prod !)
- Volume persistant : `postgres_data`

---

## 🛠️ Stack technique

| Couche | Outil | Version |
|--------|-------|---------|
| Langage | Python | 3.11 |
| ML | Scikit-Learn | 1.5.2 |
| API | FastAPI + Uvicorn | 0.115 / 0.32 |
| Validation | Pydantic | 2.9 |
| Tracking | MLflow | 2.17 |
| Base de données | PostgreSQL | 16 |
| Tests | Pytest | 8.3 |
| Conteneurisation | Docker + Compose | latest |
| CI/CD | Jenkins | LTS |
| VCS | Git + GitHub | — |

---

## ❓ Troubleshooting

### 🐳 Docker

| Problème | Solution |
|----------|----------|
| `Cannot connect to Docker daemon` | Démarrer Docker Desktop |
| `port is already allocated` | Changer le port hôte dans `docker-compose.yml` |
| MLflow crash au démarrage | Attendre que Postgres soit prêt (déjà géré via `depends_on.condition`) |

### 🔧 Jenkins

| Problème | Solution |
|----------|----------|
| `docker: command not found` dans le pipeline | Rebuild avec `Dockerfile.jenkins` (contient Docker CLI) |
| `permission denied on docker.sock` | Utiliser `user: root` dans `docker-compose.jenkins.yml` |
| `Authentication failed` (GitHub) | Vérifier / régénérer le PAT dans Manage Jenkins → Credentials |
| Pipeline ne se déclenche pas | Vérifier "Poll SCM" ou webhook GitHub |
| `Cannot connect to mlflow` | Utiliser `host.docker.internal` (Windows/Mac) au lieu de `mlflow` |

### 🐍 Python

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError` | Activer le venv : `source .venv/bin/activate` |
| MLflow refuse le file store | Utiliser SQLite en local : `sqlite:///mlflow.db` (déjà configuré) |
| `FileNotFoundError: breast_cancer.csv` | Lancer `python src/create_dataset.py` d'abord |

---

## 📚 Documentation

- 📄 [Git Cheat Sheet](docs/git-cheatsheet.md)
- 🔗 [FastAPI](https://fastapi.tiangolo.com/)
- 🔗 [MLflow](https://mlflow.org/docs/latest/index.html)
- 🔗 [Docker Compose](https://docs.docker.com/compose/)
- 🔗 [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/)

---

## 📝 Licence

Projet pédagogique — libre d'usage.

---

## ✍️ Auteur

Projet réalisé dans le cadre d'un apprentissage MLOps / CI/CD.

**Made with ❤️ using Python, Docker & Jenkins**
