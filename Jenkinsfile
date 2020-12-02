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
        stage('Deployement stage') {
            when {
                branch 'devel'
            }
            environment {
                GITHUB_TOKEN = credentials('6d8ec6ab-5977-4fa6-b526-38761f6505aa')
                GITHUB_WEBHOOK_SECRET = credentials('de3eef8f-3bb3-4720-9b8c-a69dfc07d74a')
                SECRET_KEY = credentials('ccf12244-6b8f-46ad-9640-e97350eaf1e1')
                SLACK_SIGNING_SECRET = credentials('4d93a3a4-fccc-420a-be63-4b786a0d84f7')
            }
            steps {
                sh '''
                    sed -e "s#GITHUB_TOKEN#$GITHUB_TOKEN#g" \
                        -e "s#GITHUB_WEBHOOK_SECRET#$GITHUB_WEBHOOK_SECRET#g" \
                        -e "s#SECRET_KEY#$SECRET_KEY#g" \
                        -e "s#SLACK_SIGNING_SECRET#$SLACK_SIGNING_SECRET#g" \
                        helm/values_common.in.yaml > helm/values_common.yaml
                '''
                sh 'make build TARGET=prod'
                sh 'make ecr_login'
                sh 'make ecr_push'
                sh 'make helm_install'
            }
        }
    }
}
