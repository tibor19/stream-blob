import unittest
import os
from unittest.mock import patch, MagicMock
from function_app import validate_blob_name, get_blob_service_client


class TestBlobNameValidation(unittest.TestCase):
    """Test cases for blob name validation"""
    
    def test_valid_blob_name(self):
        """Test valid blob name patterns"""
        valid_names = [
            "2025-12-04-abc123def456xyz789ab",
            "2024-01-01-12345678901234567890",
            "2023-12-31-aBcDeFgHiJkLmNoPqRsT",
            "2025-06-15-00000000000000000000",
            "2025-12-04-ABCDEFGHIJ1234567890"
        ]
        
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(
                    validate_blob_name(name),
                    f"Expected {name} to be valid"
                )
    
    def test_invalid_blob_name_wrong_date_format(self):
        """Test blob names with incorrect date format"""
        invalid_names = [
            "25-12-04-abc123def456xyz789ab",  # Year too short
            "2025-1-04-abc123def456xyz789ab",  # Month single digit
            "2025-12-4-abc123def456xyz789ab",  # Day single digit
            "20251204-abc123def456xyz789ab",  # No dashes in date
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(
                    validate_blob_name(name),
                    f"Expected {name} to be invalid"
                )
    
    def test_invalid_blob_name_wrong_suffix_length(self):
        """Test blob names with incorrect suffix length"""
        invalid_names = [
            "2025-12-04-abc123def456xyz789",  # 19 chars (too short)
            "2025-12-04-abc123def456xyz789abc",  # 21 chars (too long)
            "2025-12-04-abc",  # Way too short
            "2025-12-04-",  # Empty suffix
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(
                    validate_blob_name(name),
                    f"Expected {name} to be invalid"
                )
    
    def test_invalid_blob_name_special_characters(self):
        """Test blob names with special characters in suffix"""
        invalid_names = [
            "2025-12-04-abc123def456xyz789!@",  # Special chars
            "2025-12-04-abc123def456xyz789 b",  # Space
            "2025-12-04-abc123def456xyz789-b",  # Dash
            "2025-12-04-abc123def456xyz789_b",  # Underscore
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(
                    validate_blob_name(name),
                    f"Expected {name} to be invalid"
                )
    
    def test_invalid_blob_name_empty_or_none(self):
        """Test empty or None blob names"""
        invalid_names = [
            "",  # Empty string
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(
                    validate_blob_name(name),
                    f"Expected {name} to be invalid"
                )


class TestManagedIdentityAuthentication(unittest.TestCase):
    """Test cases for Managed Identity authentication configuration"""
    
    def test_get_blob_service_client_requires_storage_account_name(self):
        """Test that STORAGE_ACCOUNT_NAME environment variable is required"""
        # Ensure STORAGE_ACCOUNT_NAME is not set
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                get_blob_service_client()
            
            self.assertIn("STORAGE_ACCOUNT_NAME", str(context.exception))
    
    @patch('function_app.BlobServiceClient')
    @patch('function_app.DefaultAzureCredential')
    def test_get_blob_service_client_with_system_assigned_identity(self, mock_credential, mock_blob_client):
        """Test BlobServiceClient creation with system-assigned identity (no AZURE_CLIENT_ID)"""
        # Set only STORAGE_ACCOUNT_NAME
        with patch.dict(os.environ, {'STORAGE_ACCOUNT_NAME': 'teststorage'}, clear=True):
            mock_cred_instance = MagicMock()
            mock_credential.return_value = mock_cred_instance
            
            client = get_blob_service_client()
            
            # Verify DefaultAzureCredential was called
            mock_credential.assert_called_once()
            
            # Verify BlobServiceClient was called with correct URL and credential
            mock_blob_client.assert_called_once_with(
                "https://teststorage.blob.core.windows.net",
                credential=mock_cred_instance
            )
    
    @patch('function_app.BlobServiceClient')
    @patch('function_app.DefaultAzureCredential')
    def test_get_blob_service_client_with_user_assigned_identity(self, mock_credential, mock_blob_client):
        """Test BlobServiceClient creation with user-assigned identity (AZURE_CLIENT_ID set)"""
        # Set both STORAGE_ACCOUNT_NAME and AZURE_CLIENT_ID
        with patch.dict(os.environ, {
            'STORAGE_ACCOUNT_NAME': 'teststorage',
            'AZURE_CLIENT_ID': '12345678-1234-1234-1234-123456789abc'
        }, clear=True):
            mock_cred_instance = MagicMock()
            mock_credential.return_value = mock_cred_instance
            
            client = get_blob_service_client()
            
            # Verify DefaultAzureCredential was called
            # Note: DefaultAzureCredential automatically detects AZURE_CLIENT_ID from environment
            mock_credential.assert_called_once()
            
            # Verify BlobServiceClient was called with correct URL and credential
            mock_blob_client.assert_called_once_with(
                "https://teststorage.blob.core.windows.net",
                credential=mock_cred_instance
            )


if __name__ == '__main__':
    unittest.main()

