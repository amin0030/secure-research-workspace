
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Python Version') {
            steps {
                sh 'python3 --version'
            }
        }

        stage('Python Syntax Check') {
            steps {
                sh '''
                    rm -rf ci-reports
                    mkdir -p ci-reports
                    python3 -m compileall -q services packages tests
                '''
            }
        }

        stage('Helper Integrity Gate') {
            steps {
                sh 'python3 scripts/verify_helper_integrity.py'
            }
        }

        stage('Install Test Dependencies') {
            steps {
                sh '''
                    python3 -m venv .ci-venv
                    .ci-venv/bin/python -m pip install -r services/confirmation_service/requirements.txt
                    .ci-venv/bin/python -m pip install ./packages/campus_confirmation httpx==0.28.1 bandit==1.9.4 pip-audit==2.10.1
                '''
            }
        }

        stage('SAST - Bandit') {
            steps {
                sh '''
                    .ci-venv/bin/bandit -r services packages/campus_confirmation/src -ll -ii -f json -o ci-reports/bandit.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ci-reports/bandit.json', allowEmptyArchive: true
                }
            }
        }

        stage('SCA - Dependency Audit') {
            steps {
                sh '''
                    .ci-venv/bin/pip-audit --strict -f json -o ci-reports/app-api-audit.json -r services/app_api/requirements.txt
                    .ci-venv/bin/pip-audit --strict -f json -o ci-reports/booking-audit.json -r services/booking_service/requirements.txt
                    .ci-venv/bin/pip-audit --strict -f json -o ci-reports/confirmation-audit.json -r services/confirmation_service/requirements.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ci-reports/*-audit.json', allowEmptyArchive: true
                }
            }
        }

        stage('Confirmation Security Tests') {
            steps {
                sh '''
                    set +e
                    .ci-venv/bin/python -m unittest discover -s tests -p "test_confirmation_scope.py" -v > ci-reports/confirmation-tests.txt 2>&1
                    result=$?
                    cat ci-reports/confirmation-tests.txt
                    exit "$result"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ci-reports/confirmation-tests.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Helper Package Tests') {
            steps {
                sh '''
                    set +e
                    .ci-venv/bin/python -m unittest discover -s tests -p "test_confirmation_helper.py" -v > ci-reports/helper-package-tests.txt 2>&1
                    result=$?
                    cat ci-reports/helper-package-tests.txt
                    exit "$result"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ci-reports/helper-package-tests.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Helper Integrity Security Tests') {
            steps {
                sh '''
                    set +e
                    .ci-venv/bin/python -m unittest discover -s tests -p "test_helper_integrity.py" -v > ci-reports/helper-integrity-tests.txt 2>&1
                    result=$?
                    cat ci-reports/helper-integrity-tests.txt
                    exit "$result"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ci-reports/helper-integrity-tests.txt', allowEmptyArchive: true
                }
            }
        }

        stage('CI Integration Security Tests') {
            steps {
                sh '''
                    set +e
                    .ci-venv/bin/python scripts/run_ci_integration.py > ci-reports/integration-tests.txt 2>&1
                    result=$?
                    cat ci-reports/integration-tests.txt
                    exit "$result"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ci-reports/integration-tests.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Build Helper Wheel Artifact') {
            steps {
                sh '''
                    mkdir -p dist
                    .ci-venv/bin/python -m pip wheel --no-deps --wheel-dir dist ./packages/campus_confirmation
                    sha256sum dist/*.whl
                '''
                archiveArtifacts artifacts: 'dist/*.whl', fingerprint: true
            }
        }
    }
}
