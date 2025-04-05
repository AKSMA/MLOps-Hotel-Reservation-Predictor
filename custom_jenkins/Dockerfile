# Use the Jenkins LTS image as the base
FROM jenkins/jenkins:lts

# Switch to root to install Docker
USER root

# Install dependencies and Docker

# Add Jenkins user to the docker group
RUN groupadd -f docker && \
    usermod -aG docker jenkins

# Ensure Docker volume exists (for Docker-in-Docker scenarios)
RUN mkdir -p /var/lib/docker
VOLUME /var/lib/docker

# Switch back to Jenkins user
USER jenkins
