# DevContainer Configuration

This directory contains the DevContainer configuration for developing this Azure Functions Python application in GitHub Codespaces or VS Code DevContainers.

## What's Included

The DevContainer provides a complete development environment with:

- **Base Image**: `mcr.microsoft.com/azure-functions/python:4-python3.11`
  - Matches the production Dockerfile for consistency
  - Pre-configured for Azure Functions development

- **Development Tools**:
  - Azure CLI for managing Azure resources
  - Azure Functions Core Tools for local function testing
  - Python 3.11 runtime

- **VS Code Extensions**:
  - Python extension with IntelliSense
  - Pylance language server for enhanced Python support
  - Azure Functions extension for function management
  - Black formatter for code formatting
  - Pylint for code linting

- **Pre-configured Settings**:
  - Automatic code formatting on save with Black
  - Pylint enabled for code quality checks
  - Port 7071 forwarded for Azure Functions runtime
  - Python dependencies auto-installed after container creation

## Getting Started

### Using GitHub Codespaces

1. Navigate to the repository on GitHub
2. Click the "Code" button
3. Select the "Codespaces" tab
4. Click "Create codespace on [branch]"
5. Wait for the container to build and initialize
6. The environment will be ready with all dependencies installed

### Using VS Code DevContainers

#### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Visual Studio Code](https://code.visualstudio.com/) installed
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed

#### Steps
1. Clone this repository
2. Open the folder in VS Code
3. When prompted, click "Reopen in Container" 
   - Or use Command Palette (F1) → "Dev Containers: Reopen in Container"
4. Wait for the container to build and initialize
5. The environment will be ready with all dependencies installed

## Development Workflow

### Running Functions Locally

Once the container is running, you can start the Azure Functions runtime:

```bash
func start
```

The function will be available at `http://localhost:7071`

### Testing the Function

Run the unit tests:

```bash
python -m unittest test_function_app.py -v
```

### Making Code Changes

1. Edit your code in VS Code
2. Files are automatically formatted on save with Black
3. Pylint will highlight any code quality issues
4. Test your changes with `func start` or unit tests

### Environment Variables

For local development, create a `local.settings.json` file in the workspace root:

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

**Note**: This file is excluded from version control via `.gitignore`.

## Customization

### Adding More VS Code Extensions

Edit `.devcontainer/devcontainer.json` and add extension IDs to the `customizations.vscode.extensions` array:

```json
"extensions": [
  "ms-python.python",
  "your-extension-id"
]
```

### Modifying Python Settings

Edit the `customizations.vscode.settings` section in `devcontainer.json`:

```json
"settings": {
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "your-setting": "value"
}
```

### Installing Additional Tools

Modify the `postCreateCommand` in `devcontainer.json`:

```json
"postCreateCommand": "pip install -r requirements.txt && pip install your-package"
```

Or add additional features to the `features` section for system-level tools.

## Troubleshooting

### Container Won't Start
- Ensure Docker Desktop is running
- Check Docker has sufficient resources allocated
- Try rebuilding the container: Command Palette → "Dev Containers: Rebuild Container"

### Extensions Not Loading
- Rebuild the container to ensure extensions are installed
- Check the DevContainer logs for any errors

### Port 7071 Already in Use
- Stop any other Azure Functions instances running locally
- Or modify the port in `devcontainer.json` if needed

### Python Dependencies Not Installed
- The `postCreateCommand` runs automatically after container creation
- If it failed, manually run: `pip install -r requirements.txt`
- Check the DevContainer creation logs for errors

## Resources

- [DevContainers Documentation](https://containers.dev/)
- [VS Code DevContainers](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces](https://github.com/features/codespaces)
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
