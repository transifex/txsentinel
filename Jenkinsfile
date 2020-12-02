pipeline {
    agent any
    stages {
        stage('Test stage') {
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
                success {
                    slackSend (
                        channel: '#devops-league',
                        message: ':white_check_mark:'
                    )
                }
                failure {
                    slackSend (
                        channel:  '#devops-league',
                        message: 'x'
                    )
                }
            }
        }
    }
}
