pipeline {
    agent any
    options {
        // Timeout counter starts AFTER agent is allocated
        timeout(time: 1, unit: 'SECONDS')
    }
    stages {
        stage('Build') {
            steps{
                poetry install
            }
        }
        stage('Test'){
            steps{
                poetry run flake8
                poetry run pytest
            }    
        }
    }
}
