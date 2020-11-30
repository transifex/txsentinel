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
                        color: 'green',
                        message: ':white_check_mark: Tests have passed'
                    )
                }
                failure {
                    slackSend (
                        channel: '#devops-league',
                        color: 'red',
                        message: ':x: Tests have failed'
                    )
                }
            }
        }
    }
}
