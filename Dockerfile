# Use an official Python runtime as the base image
FROM python:3.9-slim

<<<<<<< HEAD
# Set environment variables for Python and Flask
=======
# Set environment variables
>>>>>>> 2f339d8a94289f48a45ac5f7cba2597b747300c7
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

<<<<<<< HEAD
# Install required system tools, Java (needed for SonarQube), and SonarQube Scanner
RUN apt-get update && apt-get install -y --no-install-recommends \
    git unzip curl openjdk-11-jre && \
=======
# Install system dependencies, including Git and SonarQube Scanner
RUN apt-get update && \
    apt-get install -y --no-install-recommends git unzip curl openjdk-11-jre && \
>>>>>>> 2f339d8a94289f48a45ac5f7cba2597b747300c7
    curl -sSLo /tmp/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip && \
    unzip /tmp/sonar-scanner.zip -d /opt && \
    rm /tmp/sonar-scanner.zip && \
    mv /opt/sonar-scanner-* /opt/sonar-scanner && \
    ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

<<<<<<< HEAD
# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
=======
# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
>>>>>>> 2f339d8a94289f48a45ac5f7cba2597b747300c7
COPY . .

# Expose the port the app will run on
EXPOSE 5000

# Run the Flask application
CMD ["flask", "run"]
