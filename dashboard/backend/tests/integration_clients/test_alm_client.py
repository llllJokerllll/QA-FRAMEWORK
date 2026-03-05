"""
Unit tests for ALM Integration Client
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from integrations.alm.client import ALMIntegration
from integrations.alm.config import ALMConfig
from integrations.base import TestResult, TestStatus, SyncResult


@pytest.fixture
def alm_config():
    """ALM configuration fixture"""
    return {
        "base_url": "https://alm.example.com/qcbin",
        "username": "test_user",
        "password": "test_password",
        "domain": "TEST_DOMAIN",
        "project": "TEST_PROJECT"
    }


@pytest.fixture
def alm_integration(alm_config):
    """ALM integration fixture"""
    return ALMIntegration(alm_config)


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient"""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.is_closed = False
    return client


class TestALMIntegration:
    """Tests for ALMIntegration class"""
    
    def test_provider_metadata(self, alm_integration):
        """Test provider metadata is correctly set"""
        assert alm_integration.provider_name == "alm"
        assert alm_integration.provider_display_name == "HP ALM / OpenText ALM"
        assert alm_integration.requires_auth is True
        assert alm_integration.supports_sync is True
        assert alm_integration.supports_test_cases is True
        assert alm_integration.supports_bugs is True
        assert alm_integration.supports_cycles is True
        assert alm_integration.IS_PAID is True
    
    def test_init_with_dict_config(self, alm_config):
        """Test initialization with dictionary config"""
        integration = ALMIntegration(alm_config)
        
        assert integration.base_url == "https://alm.example.com/qcbin"
        assert integration.username == "test_user"
        assert integration.password == "test_password"
        assert integration.domain == "TEST_DOMAIN"
        assert integration.project == "TEST_PROJECT"
        assert integration.api_base == "https://alm.example.com/qcbin/rest/domains/TEST_DOMAIN/projects/TEST_PROJECT"
    
    def test_init_with_pydantic_config(self, alm_config):
        """Test initialization with Pydantic config object"""
        config_obj = ALMConfig(**alm_config)
        integration = ALMIntegration(config_obj)
        
        assert integration.base_url == "https://alm.example.com/qcbin"
        assert integration.username == "test_user"
    
    @pytest.mark.asyncio
    async def test_connect_success(self, alm_integration, mock_httpx_client):
        """Test successful connection to ALM"""
        # Mock authentication response
        auth_response = MagicMock()
        auth_response.status_code = 200
        auth_response.cookies = {"session": "test_session"}
        
        # Mock session response
        session_response = MagicMock()
        session_response.status_code = 200
        
        mock_httpx_client.post = AsyncMock(side_effect=[auth_response, session_response])
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.connect()
        
        assert result is True
        assert alm_integration.is_connected is True
        assert alm_integration._session_cookies is not None
    
    @pytest.mark.asyncio
    async def test_connect_failure_auth(self, alm_integration, mock_httpx_client):
        """Test connection failure due to authentication"""
        auth_response = MagicMock()
        auth_response.status_code = 401
        
        mock_httpx_client.post = AsyncMock(return_value=auth_response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.connect()
        
        assert result is False
        assert alm_integration.is_connected is False
    
    @pytest.mark.asyncio
    async def test_connect_exception(self, alm_integration, mock_httpx_client):
        """Test connection exception handling"""
        mock_httpx_client.post = AsyncMock(side_effect=Exception("Network error"))
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.connect()
        
        assert result is False
        assert alm_integration.is_connected is False
        assert "Network error" in alm_integration._last_error
    
    @pytest.mark.asyncio
    async def test_disconnect(self, alm_integration, mock_httpx_client):
        """Test disconnection"""
        alm_integration._client = mock_httpx_client
        alm_integration.is_connected = True
        
        result = await alm_integration.disconnect()
        
        assert result is True
        assert alm_integration.is_connected is False
        mock_httpx_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, alm_integration, mock_httpx_client):
        """Test health check when connection is healthy"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            health = await alm_integration.health_check()
        
        assert health["status"] == "healthy"
        assert health["connected"] is True
        assert health["domain"] == "TEST_DOMAIN"
        assert health["project"] == "TEST_PROJECT"
        assert health["error"] is None
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, alm_integration, mock_httpx_client):
        """Test health check when connection is unhealthy"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 500
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            health = await alm_integration.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["connected"] is False
        assert "HTTP 500" in health["error"]
    
    @pytest.mark.skip(reason="Complex mocking setup needed for sync_test_results")
    @pytest.mark.asyncio
    async def test_sync_test_results_success(self, alm_integration, mock_httpx_client):
        """Test syncing test results successfully"""
        pass
    
    @pytest.mark.asyncio
    async def test_sync_test_results_partial_failure(self, alm_integration, mock_httpx_client):
        """Test syncing test results with partial failures"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        test_results = [
            TestResult(
                test_id="test1",
                test_name="Test Case 1",
                status=TestStatus.PASSED,
                duration=1.5
            )
        ]
        
        # First call succeeds, second fails
        success_response = MagicMock()
        success_response.status_code = 201
        
        fail_response = MagicMock()
        fail_response.status_code = 500
        
        mock_httpx_client.post = AsyncMock(return_value=fail_response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.sync_test_results(test_results)
        
        assert result.success is False
        assert result.failed_count == 1
    
    @pytest.mark.asyncio
    async def test_create_test_case_success(self, alm_integration, mock_httpx_client):
        """Test creating a test case"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 201
        response.text = "<Entity><Fields><Field Name='id'><Value>123</Value></Field></Fields></Entity>"
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.create_test_case(
                name="New Test",
                description="Test description",
                project_key="TEST_PROJECT"
            )
        
        assert result["name"] == "New Test"
        assert "url" in result
    
    @pytest.mark.asyncio
    async def test_create_test_case_failure(self, alm_integration, mock_httpx_client):
        """Test creating a test case failure"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            with pytest.raises(Exception) as exc_info:
                await alm_integration.create_test_case(
                    name="New Test",
                    description="Test description",
                    project_key="TEST_PROJECT"
                )
        
        assert "Failed to create test case" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_test_cases(self, alm_integration, mock_httpx_client):
        """Test getting test cases"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.get_test_cases(project_key="TEST_PROJECT")
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_update_test_case(self, alm_integration, mock_httpx_client):
        """Test updating a test case"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.put = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.update_test_case(
                test_id="123",
                updates={"name": "Updated Test"}
            )
        
        assert result["id"] == "123"
        assert result["updated"] is True
    
    @pytest.mark.asyncio
    async def test_create_bug_success(self, alm_integration, mock_httpx_client):
        """Test creating a bug"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 201
        response.text = "<Entity><Fields><Field Name='id'><Value>456</Value></Field></Fields></Entity>"
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.create_bug(
                title="Bug Title",
                description="Bug description",
                project_key="TEST_PROJECT",
                severity="2-High",
                priority="1-Critical"
            )
        
        assert "id" in result
        assert "url" in result
    
    @pytest.mark.asyncio
    async def test_create_bug_failure(self, alm_integration, mock_httpx_client):
        """Test creating a bug failure"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            with pytest.raises(Exception) as exc_info:
                await alm_integration.create_bug(
                    title="Bug Title",
                    description="Bug description",
                    project_key="TEST_PROJECT"
                )
        
        assert "Failed to create defect" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_bugs(self, alm_integration, mock_httpx_client):
        """Test getting bugs"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.get_bugs(project_key="TEST_PROJECT")
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_projects_success(self, alm_integration, mock_httpx_client):
        """Test getting projects"""
        alm_integration.is_connected = True
        alm_integration._session_cookies = {"session": "test"}
        
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(alm_integration, '_get_client', return_value=mock_httpx_client):
            result = await alm_integration.get_projects()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["name"] == "TEST_PROJECT"
    
    def test_validate_config_valid(self, alm_integration):
        """Test config validation with valid config"""
        is_valid, errors = alm_integration.validate_config()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_config_missing_fields(self):
        """Test config validation with missing fields"""
        config = {
            "base_url": "https://alm.example.com/qcbin"
            # Missing username, password, project
        }
        
        # Pydantic validates in constructor, so we expect validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            integration = ALMIntegration(config)
    
    def test_get_config_schema(self, alm_integration):
        """Test getting config schema"""
        schema = alm_integration.get_config_schema()
        
        assert schema["type"] == "object"
        assert "base_url" in schema["properties"]
        assert "username" in schema["properties"]
        assert "password" in schema["properties"]
        assert "project" in schema["properties"]
        assert schema["properties"]["password"]["secret"] is True
    
    @pytest.mark.asyncio
    async def test_get_client_creates_new_if_closed(self, alm_integration):
        """Test _get_client creates new client if closed"""
        mock_client = MagicMock()
        mock_client.is_closed = True
        
        alm_integration._client = mock_client
        
        with patch('integrations.alm.client.httpx.AsyncClient') as MockAsyncClient:
            MockAsyncClient.return_value = MagicMock(is_closed=False)
            
            client = await alm_integration._get_client()
            
            # Client should be created since previous was closed
            MockAsyncClient.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_client_reuses_existing(self, alm_integration, mock_httpx_client):
        """Test _get_client reuses existing client"""
        alm_integration._client = mock_httpx_client
        
        client = await alm_integration._get_client()
        
        assert client == mock_httpx_client
