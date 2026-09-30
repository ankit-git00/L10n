pipeline {
    agent any

    parameters {
        string(
            name: 'LOCALES_DIR',
            defaultValue: 'locales',
            description: 'Locale directory, relative to the repository root or an absolute path'
        )
    }

    options {
        skipDefaultCheckout(true)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate') {
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    sh 'bash tools/run_checks.sh'
                }
            }
        }

        stage('Report') {
            steps {
                archiveArtifacts artifacts: 'reports/locale-report.txt', fingerprint: true
            }
        }
    }

    post {
        success {
            echo 'Locale validation completed successfully.'
        }
        failure {
            echo 'Locale validation pipeline failed. Check the archived report and console output.'
        }
    }
}
