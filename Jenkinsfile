pipeline {
    options {
        buildDiscarder logRotator(numToKeepStr: '10')
    }
    agent any
    stages {
        stage('Tests stage') {
            // RUN stage IF pull request
            when {
                changeRequest()
            }
            steps {
                sh 'make build'
                sh 'make run-tests'
            }
            post {
                always {
                    sh 'make down'
                }
            }
        }
    }
}
