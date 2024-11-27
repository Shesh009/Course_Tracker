# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install required system tools, Java (OpenJDK 17), and SonarQube Scanner
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     git unzip curl openjdk-17-jre && \
#     curl -sSLo /tmp/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip && \
#     unzip /tmp/sonar-scanner.zip -d /opt && \
#     rm /tmp/sonar-scanner.zip && \
#     mv /opt/sonar-scanner-* /opt/sonar-scanner && \
#     ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
#     rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files to the container
COPY . /app/

# Expose port 5000 for Flask app
EXPOSE 5000

# Run the Flask app when the container starts
CMD ["python", "app.py"]
