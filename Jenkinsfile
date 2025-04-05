pipeline{
    agent any

    enviroment{
        VENV_DIR='venv'
    }

    stages{
        stage('Cloning GitHub repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning GitHub repo to Jenkins...........'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/AKSMA/MLOps-Hotel-Reservation-Predictor.git']])
                }
            }
        }

        stage('Setting up our virtual enviorment and installing dependencies'){
            steps{
                script{
                    echo 'Setting up our virtual enviorment and installing dependencies...........'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install upgrade pip
                    pip install -e .
                    '''
                }
            }
        }
    }
}