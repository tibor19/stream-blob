import logging
import os
import re
from typing import Optional
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

app = func.FunctionApp()

# Blob name pattern: YYYY-MM-DD-{20 alphanumeric characters}
BLOB_NAME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}-[a-zA-Z0-9]{20}$')

def validate_blob_name(blob_name: str) -> bool:
    """
    Validate blob name against the required pattern.
    
    Pattern: YYYY-MM-DD-{20 alphanumeric characters}
    Example: 2025-12-04-abc123def456xyz789ab
    
    Args:
        blob_name: The blob name to validate
        
    Returns:
        True if valid, False otherwise
    """
    return bool(BLOB_NAME_PATTERN.match(blob_name))

def get_blob_service_client() -> BlobServiceClient:
    """
    Create a BlobServiceClient using Managed Identity authentication.
    
    Returns:
        BlobServiceClient instance
        
    Raises:
        ValueError: If required environment variables are not set
    """
    storage_account_name = os.environ.get('STORAGE_ACCOUNT_NAME')
    
    if not storage_account_name:
        raise ValueError("STORAGE_ACCOUNT_NAME environment variable is not set")
    
    # Use Managed Identity for authentication
    credential = DefaultAzureCredential()
    account_url = f"https://{storage_account_name}.blob.core.windows.net"
    
    return BlobServiceClient(account_url, credential=credential)

@app.route(route="stream-blob", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def stream_blob(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered Azure Function that streams blob content.
    
    Query Parameters:
        blob_name: Name of the blob to stream (required)
        
    Returns:
        - 200: Blob content as stream
        - 400: Invalid blob name pattern
        - 404: Blob not found
        - 500: Server error
    """
    logging.info('Processing blob stream request')
    
    # Get blob name from query parameter
    blob_name = req.params.get('blob_name')
    
    if not blob_name:
        return func.HttpResponse(
            body='{"error": "Missing required parameter: blob_name"}',
            status_code=400,
            mimetype="application/json"
        )
    
    # Validate blob name pattern
    if not validate_blob_name(blob_name):
        return func.HttpResponse(
            body=f'{{"error": "Invalid blob name pattern. Expected format: YYYY-MM-DD-{{20 alphanumeric characters}}. Example: 2025-12-04-abc123def456xyz789ab"}}',
            status_code=400,
            mimetype="application/json"
        )
    
    try:
        # Get container name from environment variable
        container_name = os.environ.get('CONTAINER_NAME')
        
        if not container_name:
            logging.error("CONTAINER_NAME environment variable is not set")
            return func.HttpResponse(
                body='{"error": "Server configuration error: CONTAINER_NAME not set"}',
                status_code=500,
                mimetype="application/json"
            )
        
        # Get blob service client with Managed Identity
        blob_service_client = get_blob_service_client()
        
        # Get blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )
        
        # Check if blob exists
        if not blob_client.exists():
            return func.HttpResponse(
                body=f'{{"error": "Blob not found: {blob_name}"}}',
                status_code=404,
                mimetype="application/json"
            )
        
        # Download blob as stream
        blob_data = blob_client.download_blob()
        
        # Get blob properties for Content-Type
        properties = blob_client.get_blob_properties()
        content_type = properties.content_settings.content_type or "application/octet-stream"
        
        # Stream the blob content
        return func.HttpResponse(
            body=blob_data.readall(),
            status_code=200,
            mimetype=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={blob_name}"
            }
        )
        
    except ResourceNotFoundError:
        logging.error(f"Blob not found: {blob_name}")
        return func.HttpResponse(
            body=f'{{"error": "Blob not found: {blob_name}"}}',
            status_code=404,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logging.error(f"Configuration error: {str(e)}")
        return func.HttpResponse(
            body=f'{{"error": "Server configuration error: {str(e)}"}}',
            status_code=500,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error streaming blob: {str(e)}")
        return func.HttpResponse(
            body=f'{{"error": "Internal server error: {str(e)}"}}',
            status_code=500,
            mimetype="application/json"
        )
    
