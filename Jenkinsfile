
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
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
    }
}
