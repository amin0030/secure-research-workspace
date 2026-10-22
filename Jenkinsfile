
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
                sh 'python3 -m compileall -q services packages tests'
            }
        }

        stage('Install Test Dependencies') {
            steps {
                sh '''
                    python3 -m venv .ci-venv
                    .ci-venv/bin/python -m pip install -r services/confirmation_service/requirements.txt
                    .ci-venv/bin/python -m pip install ./packages/campus_confirmation httpx==0.28.1 bandit==1.9.4
                '''
            }
        }

        stage('SAST - Bandit') {
            steps {
                sh '.ci-venv/bin/bandit -r services packages/campus_confirmation/src -ll -ii'
            }
        }

        stage('Confirmation Security Tests') {
            steps {
                sh '.ci-venv/bin/python -m unittest discover -s tests -p "test_confirmation_scope.py" -v'
            }
        }
    }
}
