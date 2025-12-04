# Azure Blob Storage Streaming Function

This Azure Function provides secure streaming access to Azure Blob Storage using Managed Identity authentication.

## Features

- **Managed Identity Authentication**: Secure, password-less authentication to Azure Blob Storage
- **System-Assigned and User-Assigned Identity Support**: Flexible authentication options
- **Containerized Deployment Ready**: Compatible with Azure Container Apps and containerized Azure Functions
- **Blob Name Validation**: Enforces naming pattern `YYYY-MM-DD-{20 alphanumeric characters}`
- **HTTP Streaming**: Efficiently streams blob content via HTTP GET requests

## Authentication

This function uses **Managed Identity** to authenticate with Azure Blob Storage, eliminating the need for connection strings or access keys. The `DefaultAzureCredential` from Azure Identity SDK provides automatic authentication detection.

### Supported Managed Identity Types

#### System-Assigned Managed Identity (Default)
No additional configuration required. The identity is created automatically with the Azure Function and tied to its lifecycle.

#### User-Assigned Managed Identity
Set the `AZURE_CLIENT_ID` environment variable to the client ID of your user-assigned Managed Identity.

## Environment Variables

Configure the following environment variables for the Azure Function:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `STORAGE_ACCOUNT_NAME` | Yes | Name of the Azure Storage Account | `mystorageaccount` |
| `CONTAINER_NAME` | Yes | Name of the blob container | `mycontainer` |
| `AZURE_CLIENT_ID` | No | Client ID for user-assigned Managed Identity | `12345678-1234-1234-1234-123456789abc` |

### Setting Environment Variables

**In Azure Portal:**
1. Navigate to your Function App
2. Go to Configuration → Application Settings
3. Add the required environment variables

**In Azure CLI:**
```bash
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --settings \
    STORAGE_ACCOUNT_NAME=<storage-account-name> \
    CONTAINER_NAME=<container-name>
```

**For User-Assigned Managed Identity:**
```bash
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --settings AZURE_CLIENT_ID=<client-id>
```

## Azure Setup Instructions

### 1. Enable Managed Identity

#### For System-Assigned Identity:

**Azure Portal:**
1. Navigate to your Function App
2. Go to Identity → System assigned
3. Set Status to "On" and click Save
4. Note the Object (principal) ID displayed

**Azure CLI:**
```bash
az functionapp identity assign \
  --name <function-app-name> \
  --resource-group <resource-group-name>
```

#### For User-Assigned Identity:

**Azure Portal:**
1. Create a User-Assigned Managed Identity resource
2. Navigate to your Function App → Identity → User assigned
3. Click "Add" and select your user-assigned identity
4. Note the Client ID of the identity

**Azure CLI:**
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

### 2. Assign Storage Blob Data Reader Role

Grant the Managed Identity access to read blobs from your Storage Account.

**Azure Portal:**
1. Navigate to your Storage Account
2. Go to Access Control (IAM)
3. Click "Add" → "Add role assignment"
4. Select "Storage Blob Data Reader" role
5. In the Members tab, select "Managed identity"
6. Click "Select members" and find your Function App's identity
7. Click "Review + assign"

**Azure CLI:**

For System-Assigned Identity:
```bash
# Get the principal ID of the Function App's system-assigned identity
PRINCIPAL_ID=$(az functionapp identity show \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --query principalId -o tsv)

# Get the Storage Account resource ID
STORAGE_ACCOUNT_ID=$(az storage account show \
  --name <storage-account-name> \
  --resource-group <storage-resource-group-name> \
  --query id -o tsv)

# Assign the role
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Reader" \
  --scope $STORAGE_ACCOUNT_ID
```

For User-Assigned Identity:
```bash
# Get the principal ID of the user-assigned identity
PRINCIPAL_ID=$(az identity show \
  --name <identity-name> \
  --resource-group <resource-group-name> \
  --query principalId -o tsv)

# Get the Storage Account resource ID
STORAGE_ACCOUNT_ID=$(az storage account show \
  --name <storage-account-name> \
  --resource-group <storage-resource-group-name> \
  --query id -o tsv)

# Assign the role
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Reader" \
  --scope $STORAGE_ACCOUNT_ID
```

### 3. Verify Role Assignment

```bash
az role assignment list \
  --assignee <principal-id> \
  --scope <storage-account-id> \
  --query "[?roleDefinitionName=='Storage Blob Data Reader']" -o table
```

## Containerized Deployment

This function is fully compatible with containerized deployments using Azure Container Apps or containerized Azure Functions.

### Key Considerations:

1. **Managed Identity Support**: Both Azure Container Apps and containerized Azure Functions support Managed Identity
2. **Environment Variables**: Configure environment variables in your container configuration
3. **No Code Changes Required**: The `DefaultAzureCredential` automatically detects the containerized environment

### Building the Docker Image

A `Dockerfile` is provided in the repository for building the containerized Azure Function:

```bash
# Build the Docker image
docker build -t stream-blob-function:latest .

# Test locally (without authentication)
docker run -p 8080:80 \
  -e STORAGE_ACCOUNT_NAME=<your-storage-account> \
  -e CONTAINER_NAME=<your-container> \
  stream-blob-function:latest
```

The Dockerfile uses the official Azure Functions Python 4 runtime base image with Python 3.11.

### Pushing to Azure Container Registry

```bash
# Login to Azure Container Registry
az acr login --name <registry-name>

# Tag the image
docker tag stream-blob-function:latest <registry-name>.azurecr.io/stream-blob-function:latest

# Push to Azure Container Registry
docker push <registry-name>.azurecr.io/stream-blob-function:latest
```

### Deploying to Azure Container Apps:

```bash
# Create container app with system-assigned identity
az containerapp create \
  --name <app-name> \
  --resource-group <resource-group-name> \
  --image <registry-name>.azurecr.io/stream-blob-function:latest \
  --environment <environment-name> \
  --system-assigned \
  --env-vars \
    STORAGE_ACCOUNT_NAME=<storage-account-name> \
    CONTAINER_NAME=<container-name> \
  --registry-server <registry-name>.azurecr.io
```

### Deploying to Azure Functions (Container)

```bash
# Create a Function App with container support
az functionapp create \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --storage-account <storage-account-name> \
  --deployment-container-image-name <registry-name>.azurecr.io/stream-blob-function:latest \
  --docker-registry-server-url https://<registry-name>.azurecr.io \
  --assign-identity [system]

# Configure environment variables
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group-name> \
  --settings \
    STORAGE_ACCOUNT_NAME=<storage-account-name> \
    CONTAINER_NAME=<container-name>
```

## API Usage

### Endpoint

```
GET /api/stream-blob?blob_name={blob-name}
```

### Parameters

- `blob_name` (required): Name of the blob following the pattern `YYYY-MM-DD-{20 alphanumeric characters}`
  - Example: `2025-12-04-abc123def456xyz789ab`

### Response Codes

- `200 OK`: Successfully streamed blob content
- `400 Bad Request`: Invalid blob name pattern or missing parameter
- `404 Not Found`: Blob does not exist
- `500 Internal Server Error`: Configuration or server error

### Example Request

```bash
curl "https://<function-app-name>.azurewebsites.net/api/stream-blob?blob_name=2025-12-04-abc123def456xyz789ab"
```

## Local Development

### Prerequisites

- Python 3.8 or higher
- Azure Functions Core Tools
- Azure CLI (for authentication)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "STORAGE_ACCOUNT_NAME": "<your-storage-account-name>",
    "CONTAINER_NAME": "<your-container-name>"
  }
}
```

3. Authenticate with Azure CLI:
```bash
az login
```

The `DefaultAzureCredential` will use your Azure CLI credentials for local development.

### Running Tests

```bash
python -m unittest test_function_app.py -v
```

### Running Locally

```bash
func start
```

## Security Best Practices

1. **Never use Storage Account Keys or Connection Strings**: Always use Managed Identity for production
2. **Principle of Least Privilege**: Only assign "Storage Blob Data Reader" role, not broader permissions
3. **Scope Role Assignments**: Assign roles at the Storage Account or Container level, not subscription-wide
4. **Monitor Access**: Use Azure Monitor to track blob access and authentication attempts
5. **Network Security**: Consider using Azure Private Endpoints for Storage Accounts
6. **Secure Environment Variables**: Never commit `local.settings.json` to version control

## Troubleshooting

### "STORAGE_ACCOUNT_NAME environment variable is not set"
- Ensure environment variables are configured in Function App settings
- Verify variable names match exactly (case-sensitive)

### "403 Forbidden" or Authentication Errors
- Verify Managed Identity is enabled on the Function App
- Check that "Storage Blob Data Reader" role is assigned
- Allow 5-10 minutes for role assignments to propagate
- Verify the correct Storage Account and Container names

### User-Assigned Identity Not Working
- Ensure `AZURE_CLIENT_ID` is set to the correct client ID
- Verify the user-assigned identity is assigned to the Function App
- Check role assignments are on the correct identity

### Local Development Authentication Issues
- Run `az login` and ensure you're authenticated
- Verify your Azure account has the necessary permissions
- Check that `local.settings.json` has correct Storage Account name

## Additional Resources

- [Azure Managed Identity Overview](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)
- [DefaultAzureCredential Documentation](https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential)
- [Azure Storage RBAC Roles](https://docs.microsoft.com/azure/storage/common/storage-auth-aad-rbac-portal)
- [Azure Functions Identity](https://docs.microsoft.com/azure/app-service/overview-managed-identity)

## License

[Add your license information here]
