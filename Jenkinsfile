// =====================================================
//  Jenkinsfile — Pipeline CI/CD MLOps Breast Cancer
//  7 stages : Checkout → Install → Test → Train → MLflow → Docker → Deploy
// =====================================================

pipeline {

    // ---------- 1. Agent ----------
    // 'any' = exécute sur n'importe quel agent disponible.
    // Ici on n'a qu'un agent : le master (le conteneur Jenkins lui-même).
    agent any

    // ---------- 2. Options globales ----------
    options {
        // Timeout global : le pipeline s'arrête au-delà de 30 min
        timeout(time: 30, unit: 'MINUTES')

        // Ne garde que les 10 derniers builds (économise le disque)
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Ajoute l'horodatage aux logs
        timestamps()
    }

    // ---------- 3. Variables d'environnement ----------
    environment {
        // Nom de l'image Docker à builder
        IMAGE_NAME    = 'mlops-breast-cancer-api'
        IMAGE_TAG     = "${BUILD_NUMBER}"          // ex: mlops-breast-cancer-api:12
        IMAGE_LATEST  = "${IMAGE_NAME}:latest"

        // MLflow (le serveur tourne dans docker-compose.yml, port 5000 exposé sur l'hôte)
        // host.docker.internal = le "localhost" de l'hôte, vu depuis un conteneur (Windows/Mac Docker Desktop).
        // Sur Linux natif, ajouter "--add-host=host.docker.internal:host-gateway" au run Jenkins.
        MLFLOW_TRACKING_URI    = 'http://host.docker.internal:5000'
        MLFLOW_EXPERIMENT_NAME = 'breast_cancer_rf'

        // Python : on utilise un venv dans le workspace pour l'isolation
        VENV_DIR = '.venv'
    }

    // ---------- 4. Stages ----------
    stages {

        // =========================================================
        // Stage 1 - CHECKOUT
        // =========================================================
        stage('1. Checkout') {
            steps {
                echo '===== [Stage 1] Checkout du code GitHub ====='
                // Nettoyage préalable du workspace (pour repartir propre)
                cleanWs()
                // Checkout du code de la branche courante
                checkout scm
                sh 'ls -la'
            }
        }

        // =========================================================
        // Stage 2 - INSTALL DEPENDENCIES
        // =========================================================
        stage('2. Install dependencies') {
            steps {
                echo '===== [Stage 2] Installation des dépendances Python ====='
                sh '''
                    set -e
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    python -m pip install --upgrade pip setuptools wheel
                    pip install --no-cache-dir -r requirements.txt
                    pip list
                '''
            }
        }

        // =========================================================
        // Stage 3 - RUN TESTS
        // =========================================================
        stage('3. Run tests') {
            steps {
                echo '===== [Stage 3] Exécution des tests Pytest ====='
                sh '''
                    set -e
                    . ${VENV_DIR}/bin/activate
                    pytest tests/ -v --junitxml=reports/junit.xml
                '''
            }
            post {
                always {
                    // Publie le rapport JUnit dans Jenkins (onglet "Tests")
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        // =========================================================
        // Stage 4 - TRAIN MODEL
        // =========================================================
        stage('4. Train model') {
            steps {
                echo '===== [Stage 4] Génération du dataset + entraînement ====='
                sh '''
                    set -e
                    . ${VENV_DIR}/bin/activate
                    python src/create_dataset.py
                    python src/train.py
                    ls -la models/
                '''
            }
            post {
                success {
                    // Archive le modèle pour pouvoir le retélécharger depuis l'UI Jenkins
                    archiveArtifacts artifacts: 'models/model.pkl', fingerprint: true
                }
            }
        }

        // =========================================================
        // Stage 5 - LOG TO MLFLOW
        // =========================================================
        // Note : le log MLflow est DÉJÀ fait pendant train.py (mlflow.log_metrics).
        // Ce stage sert à VÉRIFIER que le tracking a bien eu lieu
        // et à afficher les métriques du dernier run.
        stage('5. Verify MLflow logging') {
            steps {
                echo '===== [Stage 5] Vérification du logging MLflow ====='
                sh '''
                    set -e
                    . ${VENV_DIR}/bin/activate
                    python -c "
import mlflow
import os
mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db'))
client = mlflow.tracking.MlflowClient()
exp = client.get_experiment_by_name(os.environ.get('MLFLOW_EXPERIMENT_NAME', 'breast_cancer_rf'))
if exp is None:
    raise SystemExit('[ERREUR] Experiment introuvable')
runs = client.search_runs([exp.experiment_id], order_by=['start_time DESC'], max_results=1)
if not runs:
    raise SystemExit('[ERREUR] Aucun run trouvé')
r = runs[0]
print(f'[OK] Dernier run: {r.info.run_id}')
print(f'[OK] Metrics    : {r.data.metrics}')
"
                '''
            }
        }

        // =========================================================
        // Stage 6 - BUILD DOCKER IMAGE
        // =========================================================
        stage('6. Build Docker image') {
            steps {
                echo '===== [Stage 6] Construction de l\'image Docker ====='
                sh '''
                    set -e
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_LATEST} .
                    docker images | grep ${IMAGE_NAME}
                '''
            }
        }

        // =========================================================
        // Stage 7 - DEPLOY WITH DOCKER COMPOSE
        // =========================================================
        stage('7. Deploy with Docker Compose') {
            steps {
                echo '===== [Stage 7] Déploiement de la stack ====='
                sh '''
                    set -e
                    # Recrée uniquement l'API (postgres + mlflow restent up)
                    docker compose up -d --no-deps --force-recreate api
                    docker compose ps

                    # Attente + healthcheck (max 30s)
                    echo "Attente du démarrage de l'API..."
                    for i in $(seq 1 15); do
                        if curl -fsS http://localhost:8000/health > /dev/null 2>&1; then
                            echo "[OK] API up après ${i}x2s"
                            curl -s http://localhost:8000/ | python3 -m json.tool || true
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "[ERREUR] API n'a pas démarré à temps"
                    docker compose logs api
                    exit 1
                '''
            }
        }
    }

    // ---------- 5. Post actions ----------
    post {
        success {
            echo '✅ ============================================='
            echo '✅ PIPELINE RÉUSSI'
            echo "✅ Build #${BUILD_NUMBER}"
            echo "✅ Image  : ${IMAGE_NAME}:${IMAGE_TAG}"
            echo "✅ API    : http://localhost:8000"
            echo "✅ MLflow : http://localhost:5000"
            echo '✅ ============================================='
        }
        failure {
            echo '❌ ============================================='
            echo '❌ PIPELINE ÉCHOUÉ'
            echo "❌ Build #${BUILD_NUMBER}"
            echo '❌ Voir les logs ci-dessus pour identifier l\'erreur'
            echo '❌ ============================================='
        }
        always {
            // Nettoyage du venv pour économiser l'espace
            sh 'rm -rf ${VENV_DIR} reports || true'
        }
    }
}
