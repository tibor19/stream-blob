# Azure Function: Stream Blob via Managed Identity

This Azure Function streams blob content from Azure Blob Storage using Managed Identity authentication. It's designed for containerized deployment and supports both local development and Azure deployment.

## Features

- ✅ Stream blob content efficiently without loading entire file into memory
- ✅ Managed Identity authentication (system-assigned or user-assigned)
- ✅ Blob name validation with pattern: `YYYY-MM-DD-{20 alphanumeric characters}`
- ✅ Containerized deployment ready
- ✅ Configurable via environment variables
- ✅ Comprehensive error handling (400, 404, 500 status codes)

## Prerequisites

### For Local Development
- Python 3.11 or later
- Azure Functions Core Tools v4
- Azure CLI (for authentication testing)
- Docker (for containerized testing)

### For Azure Deployment
- Azure subscription
- Azure Storage Account with a container
- Azure Function App (Linux, Python 3.11)
- Managed Identity enabled on the Function App

## Environment Variables

The following environment variables must be configured:

| Variable | Description | Example |
|----------|-------------|---------|
| `STORAGE_ACCOUNT_NAME` | Name of the Azure Storage Account | `mystorageaccount` |
| `CONTAINER_NAME` | Name of the blob container | `mycontainer` |
| `FUNCTIONS_WORKER_RUNTIME` | Azure Functions runtime (always `python`) | `python` |

## Blob Name Pattern

Blobs must follow this naming pattern:
```
YYYY-MM-DD-{20 alphanumeric characters}
```

**Example valid blob names:**
- `2025-12-04-abc123def456xyz789ab`
- `2024-01-15-ABCDEFGHIJ0123456789`

## Managed Identity Setup

### 1. Enable Managed Identity on Azure Function App

**System-assigned identity:**
```bash
az functionapp identity assign \
  --name <function-app-name> \
  --resource-group <resource-group-name>
```

**User-assigned identity:**
```bash
# Create user-assigned identity
az identity create \
  --name <identity-name> \
  --resource-group <resource-group-name>

# Assign to Function App
az functionapp identity assign \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --identities <identity-resource-id>
```

### 2. Grant Storage Blob Data Reader Role

Get the principal ID of the managed identity:
```bash
# For system-assigned identity
PRINCIPAL_ID=$(az functionapp identity show \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --query principalId -o tsv)

# For user-assigned identity
PRINCIPAL_ID=$(az identity show \
  --name <identity-name> \
  --resource-group <resource-group-name> \
  --query principalId -o tsv)
```

Assign the **Storage Blob Data Reader** role:
```bash
STORAGE_ID=$(az storage account show \
  --name <storage-account-name> \
  --resource-group <resource-group-name> \
  --query id -o tsv)

az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Reader" \
  --scope $STORAGE_ID
```

**Note:** Role assignment propagation can take up to 5 minutes.

## Local Development

### 1. Clone the Repository
```bash
git clone <repository-url>
cd stream-blob
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Local Settings
Create `local.settings.json` from the example:
```bash
cp local.settings.json.example local.settings.json
```

Edit `local.settings.json` with your settings:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "STORAGE_ACCOUNT_NAME": "your-storage-account-name",
    "CONTAINER_NAME": "your-container-name"
  }
}
```

### 4. Authenticate with Azure (for local testing)
```bash
az login
```

This allows `DefaultAzureCredential` to use your Azure CLI credentials locally.

### 5. Run the Function Locally
```bash
func start
```

The function will be available at: `http://localhost:7071/api/stream-blob`

### 6. Test the Function
```bash
# Replace with a valid blob name in your container
curl "http://localhost:7071/api/stream-blob?blob_name=2025-12-04-abc123def456xyz789ab" \
  --output downloaded-blob
```

## Docker Deployment

### 1. Build Docker Image
```bash
docker build -t stream-blob-function:latest .
```

### 2. Run Container Locally
```bash
docker run -p 8080:80 \
  -e STORAGE_ACCOUNT_NAME=your-storage-account-name \
  -e CONTAINER_NAME=your-container-name \
  -e AzureWebJobsStorage="" \
  stream-blob-function:latest
```

**Note:** For local Docker testing, you need to configure authentication. The easiest approach for testing is using a connection string, but in production, use Managed Identity.

### 3. Test Docker Container
```bash
curl "http://localhost:8080/api/stream-blob?blob_name=2025-12-04-abc123def456xyz789ab" \
  --output downloaded-blob
```

## Azure Deployment

### Option 1: Deploy Container to Azure Function App

#### 1. Push Image to Azure Container Registry (ACR)
```bash
# Create ACR if not exists
az acr create \
  --name <registry-name> \
  --resource-group <resource-group-name> \
  --sku Basic \
  --admin-enabled true

# Login to ACR
az acr login --name <registry-name>

# Tag and push image
docker tag stream-blob-function:latest <registry-name>.azurecr.io/stream-blob-function:latest
docker push <registry-name>.azurecr.io/stream-blob-function:latest
```

#### 2. Create Function App with Container
```bash
az functionapp create \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --storage-account <storage-account-name> \
  --plan <app-service-plan-name> \
  --deployment-container-image-name <registry-name>.azurecr.io/stream-blob-function:latest \
  --functions-version 4 \
  --runtime python \
  --runtime-version 3.11 \
  --os-type Linux
```

#### 3. Configure Function App Settings
```bash
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --settings \
    STORAGE_ACCOUNT_NAME=<storage-account-name> \
    CONTAINER_NAME=<container-name>
```

#### 4. Enable and Configure Managed Identity
Follow the [Managed Identity Setup](#managed-identity-setup) section above.

### Option 2: Deploy Code Directly (without container)

```bash
func azure functionapp publish <function-app-name>
```

Then follow steps 3-4 from Option 1 to configure settings and managed identity.

## API Usage

### Endpoint
```
GET /api/stream-blob?blob_name={blob-name}
```

### Parameters
- `blob_name` (required): Name of the blob to stream (must match pattern)

### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Returns blob content as binary stream |
| 400 | Bad Request - Invalid or missing blob name |
| 404 | Not Found - Blob doesn't exist |
| 500 | Internal Server Error - Storage/authentication error |

### Example Requests

**Success:**
```bash
curl "https://<function-app-name>.azurewebsites.net/api/stream-blob?blob_name=2025-12-04-abc123def456xyz789ab" \
  --output myfile.bin
```

**Invalid blob name pattern:**
```bash
curl "https://<function-app-name>.azurewebsites.net/api/stream-blob?blob_name=invalid-name"
# Returns: 400 Bad Request with error message
```

**Blob not found:**
```bash
curl "https://<function-app-name>.azurewebsites.net/api/stream-blob?blob_name=2025-12-04-nonexistentblob123"
# Returns: 404 Not Found with error message
```

## Architecture

```
┌─────────────┐      HTTP GET      ┌──────────────────┐
│   Client    │ ──────────────────> │ Azure Function   │
└─────────────┘   ?blob_name=...   │  (Container)     │
                                    └──────────────────┘
                                             │
                                             │ Managed Identity
                                             ▼
                                    ┌──────────────────┐
                                    │ Azure Blob       │
                                    │ Storage          │
                                    └──────────────────┘
```

## Security Best Practices

1. **Use Managed Identity**: Never use connection strings or access keys in production
2. **Least Privilege**: Grant only "Storage Blob Data Reader" role, not "Contributor"
3. **Network Security**: Consider using Private Endpoints for storage accounts
4. **Monitoring**: Enable Application Insights for logging and diagnostics
5. **Input Validation**: The function validates blob names to prevent path traversal

## Troubleshooting

### "STORAGE_ACCOUNT_NAME environment variable is not set"
- Ensure environment variables are configured in Function App settings or `local.settings.json`

### "Server configuration error: CONTAINER_NAME not set"
- Add `CONTAINER_NAME` to Function App settings or `local.settings.json`

### 403 Forbidden / Authentication Errors
- Verify Managed Identity is enabled
- Confirm "Storage Blob Data Reader" role is assigned
- Wait 5 minutes for role assignment propagation
- Check identity has access to the correct storage account

### 404 Blob Not Found
- Verify blob exists in the container
- Check blob name matches the required pattern
- Ensure container name is correct

### Local Development Authentication Issues
- Run `az login` to authenticate Azure CLI
- Ensure you have access to the storage account
- Consider using `az account show` to verify correct subscription

## Project Structure

```
stream-blob/
├── function_app.py              # Main function implementation
├── requirements.txt             # Python dependencies
├── host.json                    # Azure Functions configuration
├── Dockerfile                   # Container definition
├── .dockerignore               # Docker build exclusions
├── local.settings.json.example # Example local configuration
└── README.md                   # This file
```

## Dependencies

- `azure-functions>=1.18.0` - Azure Functions runtime
- `azure-identity>=1.15.0` - Managed Identity authentication
- `azure-storage-blob>=12.19.0` - Azure Blob Storage SDK

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
