# Use the official Azure Functions Python base image
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Set working directory
WORKDIR /home/site/wwwroot

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function app code
COPY function_app.py .

# Copy Azure Functions configuration
COPY host.json .

# Expose the default Azure Functions port
EXPOSE 80

# The base image already has the CMD to start the Azure Functions runtime
