# Use the official lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements to leverage Docker's caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the Flask default port (5000)
EXPOSE 5000

# Define the command to run the Flask application
CMD ["python", "app.py"]
  
