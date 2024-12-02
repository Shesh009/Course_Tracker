<!-- Hello,

  This is a web application created using python-flask which is used to track your progress the course which is taken online/offline by adding your course and modules in the course by tracking them as completed or not.

  #Link for this website is : https://progress-tracker-dgg2.onrender.com/ -->

# Course Tracker Full-Stack Application

This project is a **Full-Stack Web Application** designed to host meetings and track course-related activities. The application includes the backend (Flask) and frontend components. The project integrates **SonarQube** for code quality analysis, **Docker** for containerization, and **Jenkins** for CI/CD pipelines. The deployment is managed using **ArgoCD** on a Kubernetes cluster.

---

## Table of Contents
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Jenkins Pipeline Overview](#jenkins-pipeline-overview)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Using DockerHub Image](#using-dockerhub-image)
- [SonarQube Integration](#sonarqube-integration)
- [Docker Build Process](#docker-build-process)
- [ArgoCD Deployment Process](#argocd-deployment-process)
- [Usage](#usage)

---

## Technologies Used
- **Backend**: Flask (Python)
- **Frontend**: React.js (not included in the current scope)
- **Containerization**: Docker
- **Code Quality**: SonarQube
- **Continuous Integration/Delivery**: Jenkins
- **Orchestration**: Kubernetes
- **Deployment Tool**: ArgoCD

---

## Project Structure
```
Course-Tracker/
├── app/
│   ├── app.py                # Flask backend application
│   ├── requirements.txt      # Python dependencies
│   └── other files
├── manifests/
│   ├── deployment.yml        # deployment 
│   ├── service.yml           # service configuration
├── Jenkinsfile               # CI/CD pipeline configuration
├── Dockerfile                # Docker image build configuration
└── README.md                 # Project documentation
```

---

## Prerequisites
1. **Docker**: Install Docker to build and push container images.
2. **SonarQube**: A running SonarQube server for static code analysis.
3. **Kubernetes**: A Kubernetes cluster to deploy the application.
4. **ArgoCD**: Installed and configured for GitOps deployment.
5. **Jenkins**: A running Jenkins server with Docker support.

---

## Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Shesh009/Course_Tracker_
cd Course_Tracker_
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application Locally
```bash
python app.py
```

The application should now be running on `http://localhost:5000`.

---

## Jenkins Pipeline Overview

### Jenkinsfile Stages
1. **Checkout**: Pull the latest code from the Git repository.
2. **Install Dependencies**: Install Python dependencies.
3. **Static Code Analysis**: Run SonarQube scanner to analyze the codebase.
4. **Fetch SonarQube Report**: Retrieve and display the code quality report.
5. **Build and Push Docker Image**:
   - Build the Flask app's Docker image.
   - Push the image to Docker Hub.
6. **Update Deployment File**:
   - Update the Kubernetes `deployment.yml` file with the latest Docker image tag using jenkins build number.
   - Commit and push changes to the Git repository.

### Usage
To trigger the pipeline, configure the Jenkins job with the repository and run the build.

---

## Deployment

### Deployment Configuration (`manifests/deployment.yml`)
Defines a deployment with:
- **Replicas**: 2 instances of the Flask application.
- **Container**: Uses the Docker image `sheshu009/course-tracker:<tag>`.

### Service Configuration (`manifests/service.yml`)
Defines a service with:
- **Type**: LoadBalancer to expose the application externally.
- **Port**: Maps port `80` to the Flask container's port `5000`.

### Deploy to Kubernetes
```bash
kubectl apply -f manifests/deployment.yml
kubectl apply -f manifests/service.yml
```

---

## Using DockerHub Image
Users can directly run the application using the pre-built Docker image hosted on **DockerHub**. This allows for easy setup without needing to clone the repository or build the image locally.

### Steps to Use the DockerHub Image
1. **Pull the Docker Image**:
   ```bash
   docker pull sheshu009/course-tracker:latest
   ```
2. **Run the Docker Image**:
   ```bash
   docker run -d -p 5000:5000 sheshu009/course-tracker:latest
   ```
   Use the environment files accordingly.

3. **Access the Application**:
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

The application will be up and running, ready for use!

---

## SonarQube Integration
- The `Static Code Analysis` stage in the Jenkins pipeline uses the `sonar-scanner` to analyze the code.
- The analysis includes metrics such as **code complexity**, **violations**, and **lines of code**.

#### Example Command:
```bash
sonar-scanner \
  -Dsonar.login=$SONAR_AUTH_TOKEN \
  -Dsonar.host.url=${SONAR_URL} \
  -Dsonar.projectKey=Course-Tracker \
  -Dsonar.projectVersion=v${BUILD_NUMBER}
```

---

## Docker Build Process

### Build and Push Docker Image
```bash
docker build -t <your_dockerhub_username>/course-tracker:v1 .
docker push <your_dockerhub_username>/course-tracker:v1
```
This is automatically triggered beacause of the Dockerfile present in the folder.

---

## ArgoCD Deployment Process

### Steps
1. **Sync the Application**:
   - Configure ArgoCD to sync the `manifests/` folder from the Git repository.
   - Ensure `deployment.yml` and `service.yml` are updated with the correct Docker image tag.

2. **Access the Application**:
   - After deployment, find the external IP of the service:
     ```bash
     kubectl get svc
     ```
   - Use the IP and port `80` to access the application.

---

## Usage

### Access the Application
- The application will be exposed on the external IP provided by the Kubernetes LoadBalancer or directly on `http://localhost:5000` when using the DockerHub image.

### Monitor the Application
- Use tools like `kubectl` to monitor the status of the pods and services:
  ```bash
  kubectl get pods
  kubectl get svc
  ```

---

## Additional Notes
- Ensure that your SonarQube, Docker Hub credentials, and GitHub access token are configured in Jenkins as credentials.
- ArgoCD can be configured for automatic sync for a seamless CI/CD pipeline.
<!-- - The Flask application is ready to be extended with React for frontend development. -->

---


### Images of the application

![Screenshot 2024-02-04 094210](https://github.com/Shesh009/Course_Tracker_/assets/121094754/5f1e95d1-3caa-4e98-820f-c9014bf1613c)
![Screenshot 2024-02-04 094256](https://github.com/Shesh009/Course_Tracker_/assets/121094754/afe58a3c-ecd7-4c4b-99b5-00bea54d1b52)
![Screenshot 2024-02-04 094409](https://github.com/Shesh009/Course_Tracker_/assets/121094754/b5ac63d6-2e66-4137-9320-8cca8cc7b994)
![Screenshot 2024-02-04 094620](https://github.com/Shesh009/Course_Tracker_/assets/121094754/46d35b47-5428-4ee2-a7fc-86af5e8cef6d)
![Screenshot 2024-02-04 094424](https://github.com/Shesh009/Course_Tracker_/assets/121094754/69b209a5-7525-4d1e-a6cf-280b381b597d)
![Screenshot 2024-02-04 094448](https://github.com/Shesh009/Course_Tracker_/assets/121094754/b0811d89-fd81-4e13-8e05-594b95d40807)
![Screenshot 2024-02-04 094528](https://github.com/Shesh009/Course_Tracker_/assets/121094754/eb0b1828-42f8-47f8-90bf-0ceaafdabfc0)
![Screenshot 2024-02-04 094559](https://github.com/Shesh009/Course_Tracker_/assets/121094754/c625e7e2-b088-46b6-9118-e4c28621ede7)
