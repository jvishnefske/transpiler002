pipeline {
    agent any
    options {
        // Timeout counter starts AFTER agent is allocated
        timeout(time: 1, unit: 'SECONDS')
    }
    stages {
        stage('Build') {
            steps{
                sh 'poetry install'
            }
        }
        stage('Test'){
            steps{
                sh 'poetry run flake8'
                sh 'poetry run pytest'
            }    
        }
    }
}
