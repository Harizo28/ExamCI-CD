// =====================================================
//  Jenkinsfile — Pipeline CI/CD MLOps Breast Cancer
//  7 stages : Checkout → Install → Test → Train → MLflow → Docker → Deploy
// =====================================================

pipeline {

    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
        IMAGE_NAME    = 'mlops-breast-cancer-api'
        IMAGE_TAG     = "${BUILD_NUMBER}"
        IMAGE_LATEST  = "${IMAGE_NAME}:latest"
        MLFLOW_TRACKING_URI    = 'http://host.docker.internal:5000'
        MLFLOW_EXPERIMENT_NAME = 'breast_cancer_rf'
        VENV_DIR = '.venv'
    }

    stages {

        stage('1. Checkout') {
            steps {
                echo '===== [Stage 1] Checkout du code GitHub ====='
                cleanWs()
                checkout scm
                sh 'ls -la'
            }
        }

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
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

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
                    archiveArtifacts artifacts: 'models/model.pkl', fingerprint: true
                }
            }
        }

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

        stage('7. Deploy with Docker Compose') {
            steps {
                echo '===== [Stage 7] Déploiement de la stack ====='
                sh '''
                    set -e
                    docker rm -f mlops_api 2>/dev/null || true
                    docker compose -p mlops-breast-cancer up -d --no-deps --force-recreate api
                    docker compose -p mlops-breast-cancer ps

                    echo "Attente du démarrage de l'API..."
                    for i in $(seq 1 20); do
                        if curl -fsS http://host.docker.internal:8000/health > /dev/null 2>&1; then
                            echo "[OK] API up après ${i}x2s"
                            curl -s http://host.docker.internal:8000/ | python3 -m json.tool || true
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "[ERREUR] API n'a pas démarré à temps"
                    docker compose -p mlops-breast-cancer logs api
                    exit 1
                '''
            }
        }
    }

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
            sh 'rm -rf ${VENV_DIR} reports || true'
        }
    }
}