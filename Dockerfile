# Use the official Azure Functions Python base image
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Set environment variables for Azure Functions
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Copy requirements file and install dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the function app code
COPY . /home/site/wwwroot

# Set working directory
WORKDIR /home/site/wwwroot
