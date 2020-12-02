pipeline {
    agent any
    stages {
        stage('Tests stage') {
            when {
                changeRequest()
            }
            steps {
                sh 'echo Hello workshop!'
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
                        message: ':white_check_mark: Hi tests have passed^^'
                    )
                }
                failure {
                    slackSend (
                        channel: '#devops-league',
                        message: ':x: Bye tests have failed :('
                    )
                }
            }
        }
    }
}
