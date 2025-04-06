pipeline{
    agent any

    environment{
        VENV_DIR='venv'
        GCP_PROJECT='mlops-455510'
        GCLOUD_PATH='/var/jenkins_home/google-cloud-sdk/bin'
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
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key', variable:'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script{
                        echo 'Building and Pushing Docker Image to GCR...........'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/hotel-reservation-predictor:latest .

                        docker push gcr.io/${GCP_PROJECT}/hotel-reservation-predictor:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to Google CLoud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key', variable:'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script{
                        echo 'Deploy to Google CLoud Run...........'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy hotel-reservation-predictor \
                            --image=gcr.io/${GCP_PROJECT}/hotel-reservation-predictor:latest \
                            --platform=managed \
                            --region=us-central1 \
                            --allow-unauthenticated
                        '''
                    }
                }
            }
        }
    }
}