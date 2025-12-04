import unittest
import os
import json


class TestContainerization(unittest.TestCase):
    """Test cases for containerization setup"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_path = os.path.dirname(os.path.abspath(__file__))
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile_path = os.path.join(self.base_path, 'Dockerfile')
        self.assertTrue(os.path.exists(dockerfile_path), "Dockerfile should exist")
    
    def test_dockerfile_uses_correct_base_image(self):
        """Test that Dockerfile uses Azure Functions Python base image"""
        dockerfile_path = os.path.join(self.base_path, 'Dockerfile')
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        self.assertIn('mcr.microsoft.com/azure-functions/python', content,
                     "Dockerfile should use Azure Functions Python base image")
        self.assertIn('4-python3.11', content,
                     "Dockerfile should use Python 3.11")
    
    def test_dockerfile_sets_required_env_vars(self):
        """Test that Dockerfile sets required environment variables"""
        dockerfile_path = os.path.join(self.base_path, 'Dockerfile')
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        self.assertIn('AzureWebJobsScriptRoot=/home/site/wwwroot', content,
                     "Dockerfile should set AzureWebJobsScriptRoot")
        self.assertIn('AzureFunctionsJobHost__Logging__Console__IsEnabled=true', content,
                     "Dockerfile should enable console logging")
    
    def test_dockerfile_installs_requirements(self):
        """Test that Dockerfile installs requirements"""
        dockerfile_path = os.path.join(self.base_path, 'Dockerfile')
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        self.assertIn('COPY requirements.txt', content,
                     "Dockerfile should copy requirements.txt")
        self.assertIn('pip install', content,
                     "Dockerfile should install Python packages")
    
    def test_dockerignore_exists(self):
        """Test that .dockerignore exists"""
        dockerignore_path = os.path.join(self.base_path, '.dockerignore')
        self.assertTrue(os.path.exists(dockerignore_path), ".dockerignore should exist")
    
    def test_dockerignore_excludes_common_files(self):
        """Test that .dockerignore excludes common unnecessary files"""
        dockerignore_path = os.path.join(self.base_path, '.dockerignore')
        with open(dockerignore_path, 'r') as f:
            content = f.read()
        
        # Check for common exclusions
        self.assertIn('__pycache__', content,
                     ".dockerignore should exclude __pycache__")
        self.assertIn('.git', content,
                     ".dockerignore should exclude .git")
        self.assertIn('test_', content,
                     ".dockerignore should exclude test files")
    
    def test_host_json_exists(self):
        """Test that host.json exists"""
        host_json_path = os.path.join(self.base_path, 'host.json')
        self.assertTrue(os.path.exists(host_json_path), "host.json should exist")
    
    def test_host_json_is_valid_json(self):
        """Test that host.json is valid JSON"""
        host_json_path = os.path.join(self.base_path, 'host.json')
        with open(host_json_path, 'r') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError as e:
                self.fail(f"host.json is not valid JSON: {e}")
    
    def test_host_json_has_required_fields(self):
        """Test that host.json has required Azure Functions configuration"""
        host_json_path = os.path.join(self.base_path, 'host.json')
        with open(host_json_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn('version', config, "host.json should have version field")
        self.assertEqual(config['version'], '2.0', "host.json should use version 2.0")
    
    def test_host_json_has_extension_bundle(self):
        """Test that host.json has extension bundle configuration"""
        host_json_path = os.path.join(self.base_path, 'host.json')
        with open(host_json_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn('extensionBundle', config, "host.json should have extensionBundle")
        self.assertIn('id', config['extensionBundle'], "extensionBundle should have id")
        self.assertEqual(config['extensionBundle']['id'], 
                        'Microsoft.Azure.Functions.ExtensionBundle',
                        "extensionBundle should use Microsoft.Azure.Functions.ExtensionBundle")
    
    def test_requirements_txt_exists(self):
        """Test that requirements.txt exists"""
        requirements_path = os.path.join(self.base_path, 'requirements.txt')
        self.assertTrue(os.path.exists(requirements_path), "requirements.txt should exist")
    
    def test_requirements_txt_has_azure_dependencies(self):
        """Test that requirements.txt contains all required Azure dependencies"""
        requirements_path = os.path.join(self.base_path, 'requirements.txt')
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for required Azure packages
        self.assertIn('azure-functions', content,
                     "requirements.txt should include azure-functions")
        self.assertIn('azure-identity', content,
                     "requirements.txt should include azure-identity")
        self.assertIn('azure-storage-blob', content,
                     "requirements.txt should include azure-storage-blob")
    
    def test_requirements_txt_has_minimum_versions(self):
        """Test that requirements.txt specifies minimum versions"""
        requirements_path = os.path.join(self.base_path, 'requirements.txt')
        with open(requirements_path, 'r') as f:
            lines = f.readlines()
        
        # Check that each package has a version constraint
        # Valid PEP 440 version specifiers: ==, !=, >=, <=, >, <, ~=, ===
        version_specifiers = ['==', '!=', '>=', '<=', '>', '<', '~=', '===']
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                has_version = any(spec in line for spec in version_specifiers)
                self.assertTrue(has_version,
                              f"Package {line} should have a version constraint")


if __name__ == '__main__':
    unittest.main()
