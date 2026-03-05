"""
Unit tests for Azure DevOps Integration Client
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import base64

from integrations.azure_devops.client import AzureDevOpsIntegration
from integrations.azure_devops.config import AzureDevOpsConfig
from integrations.base import TestResult, TestStatus, SyncResult


@pytest.fixture
def ado_config():
    """Azure DevOps configuration fixture"""
    return {
        "organization_url": "https://dev.azure.com/testorg",
        "project_name": "TestProject",
        "personal_access_token": "test_pat_token_12345",
        "area_path": "TestProject\\Area1",
        "iteration_path": "TestProject\\Sprint1"
    }


@pytest.fixture
def ado_integration(ado_config):
    """Azure DevOps integration fixture"""
    return AzureDevOpsIntegration(ado_config)


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient"""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.is_closed = False
    return client


class TestAzureDevOpsIntegration:
    """Tests for AzureDevOpsIntegration class"""
    
    def test_provider_metadata(self, ado_integration):
        """Test provider metadata is correctly set"""
        assert ado_integration.provider_name == "azure_devops"
        assert ado_integration.provider_display_name == "Azure DevOps"
        assert ado_integration.requires_auth is True
        assert ado_integration.supports_sync is True
        assert ado_integration.supports_test_cases is True
        assert ado_integration.supports_bugs is True
        assert ado_integration.supports_cycles is True
    
    def test_init_with_dict_config(self, ado_config):
        """Test initialization with dictionary config"""
        integration = AzureDevOpsIntegration(ado_config)
        
        assert integration.organization_url == "https://dev.azure.com/testorg"
        assert integration.project_name == "TestProject"
        assert integration.personal_access_token == "test_pat_token_12345"
        assert integration.area_path == "TestProject\\Area1"
        assert integration.iteration_path == "TestProject\\Sprint1"
        assert integration.api_base == "https://dev.azure.com/testorg/TestProject/_apis"
    
    def test_init_with_pydantic_config(self, ado_config):
        """Test initialization with Pydantic config object"""
        config_obj = AzureDevOpsConfig(**ado_config)
        integration = AzureDevOpsIntegration(config_obj)
        
        assert integration.organization_url == "https://dev.azure.com/testorg"
        assert integration.project_name == "TestProject"
    
    def test_auth_header_encoding(self, ado_integration):
        """Test authentication header is correctly encoded"""
        expected_auth_string = f":{ado_integration.personal_access_token}"
        expected_b64 = base64.b64encode(expected_auth_string.encode('ascii')).decode('ascii')
        
        assert ado_integration.headers['Authorization'] == f'Basic {expected_b64}'
    
    @pytest.mark.asyncio
    async def test_connect_success(self, ado_integration, mock_httpx_client):
        """Test successful connection to Azure DevOps"""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"name": "TestProject", "id": "project-id-123"}
        
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.connect()
        
        assert result is True
        assert ado_integration.is_connected is True
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, ado_integration, mock_httpx_client):
        """Test connection failure"""
        response = MagicMock()
        response.status_code = 401
        
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.connect()
        
        assert result is False
        assert ado_integration.is_connected is False
        assert "401" in ado_integration._last_error
    
    @pytest.mark.asyncio
    async def test_connect_exception(self, ado_integration, mock_httpx_client):
        """Test connection exception handling"""
        mock_httpx_client.get = AsyncMock(side_effect=Exception("Network error"))
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.connect()
        
        assert result is False
        assert ado_integration.is_connected is False
        assert "Network error" in ado_integration._last_error
    
    @pytest.mark.asyncio
    async def test_disconnect(self, ado_integration, mock_httpx_client):
        """Test disconnection"""
        ado_integration._client = mock_httpx_client
        ado_integration.is_connected = True
        
        result = await ado_integration.disconnect()
        
        assert result is True
        assert ado_integration.is_connected is False
        mock_httpx_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, ado_integration, mock_httpx_client):
        """Test health check when connection is healthy"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"name": "TestProject", "id": "project-id"}
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            health = await ado_integration.health_check()
        
        assert health["status"] == "healthy"
        assert health["connected"] is True
        assert health["project"] == "TestProject"
        assert health["error"] is None
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, ado_integration, mock_httpx_client):
        """Test health check when connection is unhealthy"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 500
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            health = await ado_integration.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["connected"] is False
        assert "HTTP 500" in health["error"]
    
    @pytest.mark.asyncio
    async def test_sync_test_results_success(self, ado_integration, mock_httpx_client):
        """Test syncing test results successfully"""
        ado_integration.is_connected = True
        
        test_results = [
            TestResult(
                test_id="test1",
                test_name="Test Case 1",
                status=TestStatus.PASSED,
                duration=1.5
            ),
            TestResult(
                test_id="test2",
                test_name="Test Case 2",
                status=TestStatus.FAILED,
                duration=2.0,
                error="Assertion failed"
            )
        ]
        
        # Mock bug creation for failed test
        bug_response = MagicMock()
        bug_response.status_code = 200
        bug_response.json.return_value = {
            "id": 123,
            "_links": {"html": {"href": "https://dev.azure.com/testorg/bug/123"}}
        }
        
        mock_httpx_client.patch = AsyncMock(return_value=bug_response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.sync_test_results(test_results)
        
        # Check that at least one result was synced
        assert result.synced_count >= 1
    
    @pytest.mark.asyncio
    async def test_sync_test_results_with_cycle(self, ado_integration, mock_httpx_client):
        """Test syncing test results with test run creation"""
        ado_integration.is_connected = True
        
        test_results = [
            TestResult(
                test_id="test1",
                test_name="Test Case 1",
                status=TestStatus.PASSED,
                duration=1.5
            )
        ]
        
        # Mock project ID lookup
        project_response = MagicMock()
        project_response.status_code = 200
        project_response.json.return_value = {"id": "project-id-123"}
        
        # Mock test run creation
        test_run_response = MagicMock()
        test_run_response.status_code = 200
        test_run_response.json.return_value = {"id": "run-123"}
        
        # Mock test result addition
        result_response = MagicMock()
        result_response.status_code = 200
        
        mock_httpx_client.get = AsyncMock(return_value=project_response)
        mock_httpx_client.post = AsyncMock(return_value=test_run_response)
        mock_httpx_client.patch = AsyncMock(return_value=result_response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.sync_test_results(
                test_results,
                cycle_name="Sprint 1 Test Run"
            )
        
        assert result.synced_count == 1
    
    @pytest.mark.asyncio
    async def test_create_test_case_success(self, ado_integration, mock_httpx_client):
        """Test creating a test case"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "id": 456,
            "_links": {"html": {"href": "https://dev.azure.com/testorg/workitem/456"}}
        }
        mock_httpx_client.patch = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.create_test_case(
                name="New Test Case",
                description="Test description",
                project_key="TestProject",
                labels=["smoke", "regression"]
            )
        
        assert result["id"] == 456
        assert result["name"] == "New Test Case"
        assert "url" in result
    
    @pytest.mark.asyncio
    async def test_create_test_case_failure(self, ado_integration, mock_httpx_client):
        """Test creating a test case failure"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        mock_httpx_client.patch = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            with pytest.raises(Exception) as exc_info:
                await ado_integration.create_test_case(
                    name="New Test Case",
                    description="Test description",
                    project_key="TestProject"
                )
        
        assert "Failed to create test case" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_test_cases_success(self, ado_integration, mock_httpx_client):
        """Test getting test cases"""
        ado_integration.is_connected = True
        
        wiql_response = MagicMock()
        wiql_response.status_code = 200
        wiql_response.json.return_value = {
            "workItems": [{"id": 100}, {"id": 101}]
        }
        
        detail_response1 = MagicMock()
        detail_response1.status_code = 200
        detail_response1.json.return_value = {
            "id": 100,
            "fields": [
                {"fieldName": "Title", "value": "Test Case 1"},
                {"fieldName": "State", "value": "Active"},
                {"fieldName": "Tags", "value": "smoke"}
            ],
            "_links": {"html": {"href": "https://dev.azure.com/testorg/workitem/100"}}
        }
        
        detail_response2 = MagicMock()
        detail_response2.status_code = 200
        detail_response2.json.return_value = {
            "id": 101,
            "fields": [
                {"fieldName": "Title", "value": "Test Case 2"},
                {"fieldName": "State", "value": "Active"}
            ],
            "_links": {"html": {"href": "https://dev.azure.com/testorg/workitem/101"}}
        }
        
        mock_httpx_client.post = AsyncMock(return_value=wiql_response)
        mock_httpx_client.get = AsyncMock(side_effect=[detail_response1, detail_response2])
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.get_test_cases(project_key="TestProject")
        
        assert len(result) == 2
        assert result[0]["id"] == 100
        assert result[0]["name"] == "Test Case 1"
    
    @pytest.mark.asyncio
    async def test_update_test_case_success(self, ado_integration, mock_httpx_client):
        """Test updating a test case"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.patch = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.update_test_case(
                test_id="456",
                updates={
                    "name": "Updated Test Case",
                    "description": "Updated description",
                    "labels": ["new-tag"]
                }
            )
        
        assert result["id"] == "456"
        assert result["updated"] is True
    
    @pytest.mark.asyncio
    async def test_create_bug_success(self, ado_integration, mock_httpx_client):
        """Test creating a bug"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "id": 789,
            "_links": {"html": {"href": "https://dev.azure.com/testorg/workitem/789"}}
        }
        mock_httpx_client.patch = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.create_bug(
                title="Bug Title",
                description="Bug description",
                project_key="TestProject",
                severity="1 - Critical",
                priority=1,
                labels=["bug", "critical"]
            )
        
        assert result["id"] == 789
        assert "url" in result
    
    @pytest.mark.asyncio
    async def test_create_bug_with_test_result(self, ado_integration, mock_httpx_client):
        """Test creating a bug with test result"""
        ado_integration.is_connected = True
        
        test_result = TestResult(
            test_id="test123",
            test_name="Failing Test",
            status=TestStatus.FAILED,
            error="AssertionError"
        )
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "id": 999,
            "_links": {"html": {"href": "https://dev.azure.com/testorg/workitem/999"}}
        }
        mock_httpx_client.patch = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.create_bug(
                title="Bug from Test",
                description="Test failed",
                project_key="TestProject",
                test_result=test_result
            )
        
        assert result["id"] == 999
    
    @pytest.mark.asyncio
    async def test_get_bugs_success(self, ado_integration, mock_httpx_client):
        """Test getting bugs"""
        ado_integration.is_connected = True
        
        wiql_response = MagicMock()
        wiql_response.status_code = 200
        wiql_response.json.return_value = {
            "workItems": [{"id": 200}]
        }
        
        detail_response = MagicMock()
        detail_response.status_code = 200
        detail_response.json.return_value = {
            "id": 200,
            "fields": [
                {"fieldName": "Title", "value": "Bug 1"},
                {"fieldName": "State", "value": "Active"},
                {"fieldName": "Assigned To", "value": "John Doe"}
            ],
            "_links": {"html": {"href": "https://dev.azure.com/testorg/workitem/200"}}
        }
        
        mock_httpx_client.post = AsyncMock(return_value=wiql_response)
        mock_httpx_client.get = AsyncMock(return_value=detail_response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.get_bugs(project_key="TestProject")
        
        assert len(result) == 1
        assert result[0]["id"] == 200
        assert result[0]["title"] == "Bug 1"
    
    @pytest.mark.asyncio
    async def test_get_projects_success(self, ado_integration, mock_httpx_client):
        """Test getting projects"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "value": [
                {"id": "proj1", "name": "Project 1"},
                {"id": "proj2", "name": "Project 2"}
            ]
        }
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            result = await ado_integration.get_projects()
        
        assert len(result) == 2
        assert result[0]["key"] == "proj1"
        assert result[0]["name"] == "Project 1"
    
    def test_validate_config_valid(self, ado_integration):
        """Test config validation with valid config"""
        is_valid, errors = ado_integration.validate_config()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_config_missing_fields(self):
        """Test config validation with missing fields"""
        config = {
            "organization_url": "https://dev.azure.com/testorg"
            # Missing project_name, personal_access_token
        }
        
        # Pydantic validates in constructor, so we expect validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            integration = AzureDevOpsIntegration(config)
    
    def test_validate_config_invalid_url(self):
        """Test config validation with invalid URL format"""
        config = {
            "organization_url": "https://invalid-url.com",
            "project_name": "TestProject",
            "personal_access_token": "test_token"
        }
        
        # Pydantic validates in constructor, so we expect validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            integration = AzureDevOpsIntegration(config)
    
    def test_get_config_schema(self, ado_integration):
        """Test getting config schema"""
        schema = ado_integration.get_config_schema()
        
        assert schema["type"] == "object"
        assert "organization_url" in schema["properties"]
        assert "project_name" in schema["properties"]
        assert "personal_access_token" in schema["properties"]
        assert schema["properties"]["personal_access_token"]["secret"] is True
    
    @pytest.mark.asyncio
    async def test_get_project_id_success(self, ado_integration, mock_httpx_client):
        """Test getting project ID"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"id": "project-uuid-123"}
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            project_id = await ado_integration._get_project_id("TestProject")
        
        assert project_id == "project-uuid-123"
    
    @pytest.mark.asyncio
    async def test_get_project_id_not_found(self, ado_integration, mock_httpx_client):
        """Test getting project ID when project not found"""
        ado_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 404
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(ado_integration, '_get_client', return_value=mock_httpx_client):
            with pytest.raises(Exception) as exc_info:
                await ado_integration._get_project_id("NonExistentProject")
        
        assert "Project not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_client_creates_new_if_none(self, ado_integration):
        """Test _get_client creates new client if none exists"""
        ado_integration._client = None
        
        with patch('integrations.azure_devops.client.httpx.AsyncClient') as MockAsyncClient:
            MockAsyncClient.return_value = MagicMock(is_closed=False)
            
            client = await ado_integration._get_client()
            
            # Client should be created since none existed
            MockAsyncClient.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_client_reuses_existing(self, ado_integration, mock_httpx_client):
        """Test _get_client reuses existing client"""
        ado_integration._client = mock_httpx_client
        
        client = await ado_integration._get_client()
        
        assert client == mock_httpx_client
    
    def test_format_test_result_for_bug(self, ado_integration):
        """Test formatting test result for bug description"""
        test_result = TestResult(
            test_id="test123",
            test_name="Failing Test",
            classname="TestClass",
            status=TestStatus.FAILED,
            duration=5.0,
            error="AssertionError",
            stack_trace="at line 10",
            tags=["smoke"]
        )
        
        description = ado_integration._format_test_result_for_bug(test_result)
        
        assert "Failing Test" in description
        assert "TestClass" in description
        assert "5.0s" in description
        assert "AssertionError" in description
        assert "at line 10" in description
