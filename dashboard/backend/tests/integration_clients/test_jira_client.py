"""
Unit tests for Jira Integration Client
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from integrations.jira.client import JiraIntegration
from integrations.jira.config import JiraConfig
from integrations.base import TestResult, TestStatus, SyncResult


@pytest.fixture
def jira_config():
    """Jira configuration fixture"""
    return {
        "base_url": "https://testcompany.atlassian.net",
        "email": "test@example.com",
        "api_token": "test_api_token_12345",
        "default_project": "QA",
        "default_issue_type": "Bug",
        "default_test_issue_type": "Task",
        "auto_create_bugs": True,
        "label_prefix": "qa-framework"
    }


@pytest.fixture
def jira_integration(jira_config):
    """Jira integration fixture"""
    return JiraIntegration(jira_config)


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient"""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.is_closed = False
    return client


class TestJiraIntegration:
    """Tests for JiraIntegration class"""
    
    def test_provider_metadata(self, jira_integration):
        """Test provider metadata is correctly set"""
        assert jira_integration.provider_name == "jira"
        assert jira_integration.provider_display_name == "Jira (Atlassian)"
        assert jira_integration.requires_auth is True
        assert jira_integration.supports_sync is True
        assert jira_integration.supports_test_cases is True
        assert jira_integration.supports_bugs is True
        assert jira_integration.supports_cycles is False
    
    def test_init_with_dict_config(self, jira_config):
        """Test initialization with dictionary config"""
        integration = JiraIntegration(jira_config)
        
        assert integration.base_url == "https://testcompany.atlassian.net"
        assert integration.email == "test@example.com"
        assert integration.api_token == "test_api_token_12345"
        assert integration.auth == ("test@example.com", "test_api_token_12345")
    
    def test_init_with_pydantic_config(self, jira_config):
        """Test initialization with Pydantic config object"""
        config_obj = JiraConfig(**jira_config)
        integration = JiraIntegration(config_obj)
        
        assert integration.base_url == "https://testcompany.atlassian.net"
        assert integration.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_connect_success(self, jira_integration, mock_httpx_client):
        """Test successful connection to Jira"""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "displayName": "Test User",
            "accountId": "user-123"
        }
        
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.connect()
        
        assert result is True
        assert jira_integration.is_connected is True
        assert hasattr(jira_integration, '_current_user')
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, jira_integration, mock_httpx_client):
        """Test connection failure"""
        response = MagicMock()
        response.status_code = 401
        
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.connect()
        
        assert result is False
        assert jira_integration.is_connected is False
        assert "401" in jira_integration._last_error
    
    @pytest.mark.asyncio
    async def test_connect_exception(self, jira_integration, mock_httpx_client):
        """Test connection exception handling"""
        mock_httpx_client.get = AsyncMock(side_effect=Exception("Network error"))
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.connect()
        
        assert result is False
        assert jira_integration.is_connected is False
        assert "Network error" in jira_integration._last_error
    
    @pytest.mark.asyncio
    async def test_disconnect(self, jira_integration, mock_httpx_client):
        """Test disconnection"""
        jira_integration._client = mock_httpx_client
        jira_integration.is_connected = True
        
        result = await jira_integration.disconnect()
        
        assert result is True
        assert jira_integration.is_connected is False
        mock_httpx_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, jira_integration, mock_httpx_client):
        """Test health check when connection is healthy"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "displayName": "Test User",
            "accountId": "user-123"
        }
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            health = await jira_integration.health_check()
        
        assert health["status"] == "healthy"
        assert health["connected"] is True
        assert health["user"] == "Test User"
        assert health["account_id"] == "user-123"
        assert health["error"] is None
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, jira_integration, mock_httpx_client):
        """Test health check when connection is unhealthy"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 500
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            health = await jira_integration.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["connected"] is False
        assert "HTTP 500" in health["error"]
    
    @pytest.mark.asyncio
    async def test_sync_test_results_success_with_bug_creation(self, jira_integration, mock_httpx_client):
        """Test syncing test results with auto bug creation"""
        jira_integration.is_connected = True
        
        test_results = [
            TestResult(
                test_id="test1",
                test_name="Passing Test",
                status=TestStatus.PASSED,
                duration=1.5
            ),
            TestResult(
                test_id="test2",
                test_name="Failing Test",
                status=TestStatus.FAILED,
                duration=2.0,
                error="Assertion failed"
            )
        ]
        
        bug_response = MagicMock()
        bug_response.status_code = 201
        bug_response.json.return_value = {
            "id": "10001",
            "key": "QA-123"
        }
        mock_httpx_client.post = AsyncMock(return_value=bug_response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.sync_test_results(test_results, project_key="QA")
        
        # Check that at least one result was synced
        assert result.synced_count >= 1
    
    @pytest.mark.asyncio
    async def test_sync_test_results_with_issue_key(self, jira_integration, mock_httpx_client):
        """Test syncing test results with existing issue key"""
        jira_integration.is_connected = True
        
        test_results = [
            TestResult(
                test_id="test1",
                test_name="Passing Test",
                status=TestStatus.PASSED,
                duration=1.5,
                issue_key="QA-100"
            )
        ]
        
        comment_response = MagicMock()
        comment_response.status_code = 201
        comment_response.json.return_value = {"id": "comment-1"}
        mock_httpx_client.post = AsyncMock(return_value=comment_response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.sync_test_results(test_results, project_key="QA")
        
        assert result.synced_count == 1
    
    @pytest.mark.asyncio
    async def test_sync_test_results_no_project(self, jira_integration, mock_httpx_client):
        """Test syncing test results without project key"""
        jira_integration.is_connected = True
        jira_integration.jira_config.default_project = None
        
        test_results = [
            TestResult(
                test_id="test1",
                test_name="Test",
                status=TestStatus.PASSED,
                duration=1.5
            )
        ]
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.sync_test_results(test_results)
        
        assert result.success is False
        assert "No project key" in result.errors[0]
    
    @pytest.mark.asyncio
    async def test_create_test_case_success(self, jira_integration, mock_httpx_client):
        """Test creating a test case"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 201
        response.json.return_value = {
            "id": "10002",
            "key": "QA-124"
        }
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.create_test_case(
                name="New Test Case",
                description="Test description",
                project_key="QA",
                labels=["smoke", "regression"],
                folder="Authentication"
            )
        
        assert result["id"] == "10002"
        assert result["key"] == "QA-124"
        assert result["name"] == "New Test Case"
        assert "url" in result
    
    @pytest.mark.asyncio
    async def test_create_test_case_failure(self, jira_integration, mock_httpx_client):
        """Test creating a test case failure"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            with pytest.raises(Exception) as exc_info:
                await jira_integration.create_test_case(
                    name="New Test Case",
                    description="Test description",
                    project_key="QA"
                )
        
        assert "Failed to create test case" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_test_cases_success(self, jira_integration, mock_httpx_client):
        """Test getting test cases"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "issues": [
                {
                    "id": "10003",
                    "key": "QA-125",
                    "fields": {
                        "summary": "Test Case 1",
                        "status": {"name": "Open"},
                        "labels": ["smoke"],
                        "issuetype": {"name": "Task"}
                    }
                },
                {
                    "id": "10004",
                    "key": "QA-126",
                    "fields": {
                        "summary": "Test Case 2",
                        "status": {"name": "In Progress"},
                        "labels": ["regression"],
                        "issuetype": {"name": "Task"}
                    }
                }
            ]
        }
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.get_test_cases(
                project_key="QA",
                filters={"status": "Open"}
            )
        
        assert len(result) == 2
        assert result[0]["id"] == "10003"
        assert result[0]["name"] == "Test Case 1"
        assert result[0]["status"] == "Open"
    
    @pytest.mark.asyncio
    async def test_get_test_cases_with_folder(self, jira_integration, mock_httpx_client):
        """Test getting test cases filtered by folder"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"issues": []}
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.get_test_cases(
                project_key="QA",
                folder="Authentication"
            )
        
        # Verify the JQL includes folder label
        call_args = mock_httpx_client.post.call_args
        assert "folder:Authentication" in call_args[1]["json"]["jql"]
    
    @pytest.mark.asyncio
    async def test_update_test_case_success(self, jira_integration, mock_httpx_client):
        """Test updating a test case"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 204
        mock_httpx_client.put = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.update_test_case(
                test_id="QA-125",
                updates={
                    "name": "Updated Test Case",
                    "description": "Updated description",
                    "labels": ["new-tag"]
                }
            )
        
        assert result["id"] == "QA-125"
        assert result["updated"] is True
    
    @pytest.mark.asyncio
    async def test_update_test_case_failure(self, jira_integration, mock_httpx_client):
        """Test updating a test case failure"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        mock_httpx_client.put = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            with pytest.raises(Exception) as exc_info:
                await jira_integration.update_test_case(
                    test_id="QA-125",
                    updates={"name": "Updated Test"}
                )
        
        assert "Failed to update test case" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_bug_success(self, jira_integration, mock_httpx_client):
        """Test creating a bug"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 201
        response.json.return_value = {
            "id": "10005",
            "key": "QA-127"
        }
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.create_bug(
                title="Bug Title",
                description="Bug description",
                project_key="QA",
                severity="High",
                priority="Critical",
                labels=["bug", "critical"]
            )
        
        assert result["id"] == "10005"
        assert result["key"] == "QA-127"
        assert "url" in result
    
    @pytest.mark.asyncio
    async def test_create_bug_with_test_result(self, jira_integration, mock_httpx_client):
        """Test creating a bug with test result"""
        jira_integration.is_connected = True
        
        test_result = TestResult(
            test_id="test123",
            test_name="Failing Test",
            status=TestStatus.FAILED,
            error="AssertionError"
        )
        
        response = MagicMock()
        response.status_code = 201
        response.json.return_value = {
            "id": "10006",
            "key": "QA-128"
        }
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.create_bug(
                title="Bug from Test",
                description="Test failed",
                project_key="QA",
                test_result=test_result
            )
        
        # Verify test ID was added to labels
        call_args = mock_httpx_client.post.call_args
        labels = call_args[1]["json"]["fields"]["labels"]
        assert "test-test123" in labels
    
    @pytest.mark.asyncio
    async def test_get_bugs_success(self, jira_integration, mock_httpx_client):
        """Test getting bugs"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "issues": [
                {
                    "id": "10007",
                    "key": "QA-129",
                    "fields": {
                        "summary": "Bug 1",
                        "status": {"name": "Open"},
                        "priority": {"name": "High"},
                        "labels": ["bug"]
                    }
                }
            ]
        }
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.get_bugs(
                project_key="QA",
                status="Open"
            )
        
        assert len(result) == 1
        assert result[0]["id"] == "10007"
        assert result[0]["title"] == "Bug 1"
        assert result[0]["priority"] == "High"
    
    @pytest.mark.asyncio
    async def test_get_projects_success(self, jira_integration, mock_httpx_client):
        """Test getting projects"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = [
            {"id": "10000", "key": "QA", "name": "QA Project"},
            {"id": "10001", "key": "DEV", "name": "Dev Project"}
        ]
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.get_projects()
        
        assert len(result) == 2
        assert result[0]["key"] == "QA"
        assert result[0]["name"] == "QA Project"
    
    @pytest.mark.asyncio
    async def test_add_comment_success(self, jira_integration, mock_httpx_client):
        """Test adding a comment to an issue"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 201
        response.json.return_value = {"id": "comment-1", "body": "Test comment"}
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.add_comment(
                issue_key="QA-100",
                comment="Test comment"
            )
        
        assert result["id"] == "comment-1"
    
    @pytest.mark.asyncio
    async def test_add_comment_failure(self, jira_integration, mock_httpx_client):
        """Test adding a comment failure"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            with pytest.raises(Exception) as exc_info:
                await jira_integration.add_comment(
                    issue_key="QA-100",
                    comment="Test comment"
                )
        
        assert "Failed to add comment" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_transition_issue_success(self, jira_integration, mock_httpx_client):
        """Test transitioning an issue"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 204
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.transition_issue(
                issue_key="QA-100",
                transition_id="31"
            )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_transition_issue_failure(self, jira_integration, mock_httpx_client):
        """Test transitioning an issue failure"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 400
        mock_httpx_client.post = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.transition_issue(
                issue_key="QA-100",
                transition_id="31"
            )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_transitions_success(self, jira_integration, mock_httpx_client):
        """Test getting available transitions"""
        jira_integration.is_connected = True
        
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "transitions": [
                {"id": "31", "name": "In Progress"},
                {"id": "41", "name": "Done"}
            ]
        }
        mock_httpx_client.get = AsyncMock(return_value=response)
        
        with patch.object(jira_integration, '_get_client', return_value=mock_httpx_client):
            result = await jira_integration.get_transitions(issue_key="QA-100")
        
        assert len(result) == 2
        assert result[0]["name"] == "In Progress"
    
    def test_validate_config_valid(self, jira_integration):
        """Test config validation with valid config"""
        is_valid, errors = jira_integration.validate_config()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_config_missing_fields(self):
        """Test config validation with missing fields"""
        config = {
            "base_url": "https://testcompany.atlassian.net"
            # Missing email, api_token
        }
        
        # Pydantic validates in constructor, so we expect validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            integration = JiraIntegration(config)
    
    def test_validate_config_invalid_url(self):
        """Test config validation with non-HTTPS URL"""
        config = {
            "base_url": "http://testcompany.atlassian.net",
            "email": "test@example.com",
            "api_token": "test_token"
        }
        
        # Pydantic validates in constructor, so we expect validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            integration = JiraIntegration(config)
    
    def test_validate_config_invalid_email(self):
        """Test config validation with invalid email"""
        config = {
            "base_url": "https://testcompany.atlassian.net",
            "email": "invalid-email",
            "api_token": "test_token"
        }
        
        # Pydantic validates in constructor, so we expect validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            integration = JiraIntegration(config)
    
    def test_get_config_schema(self, jira_integration):
        """Test getting config schema"""
        schema = jira_integration.get_config_schema()
        
        assert schema["type"] == "object"
        assert "base_url" in schema["properties"]
        assert "email" in schema["properties"]
        assert "api_token" in schema["properties"]
        assert schema["properties"]["api_token"]["secret"] is True
        assert "default_project" in schema["properties"]
    
    def test_build_description(self, jira_integration):
        """Test building Atlassian Document Format description"""
        description = jira_integration._build_description("Test description")
        
        assert description["type"] == "doc"
        assert description["version"] == 1
        assert len(description["content"]) > 0
        assert description["content"][0]["type"] == "paragraph"
    
    @pytest.mark.asyncio
    async def test_get_client_creates_new_if_none(self, jira_integration):
        """Test _get_client creates new client if none exists"""
        jira_integration._client = None
        
        with patch('integrations.jira.client.httpx.AsyncClient') as MockAsyncClient:
            MockAsyncClient.return_value = MagicMock(is_closed=False)
            
            client = await jira_integration._get_client()
            
            # Client should be created since none existed
            MockAsyncClient.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_client_reuses_existing(self, jira_integration, mock_httpx_client):
        """Test _get_client reuses existing client"""
        jira_integration._client = mock_httpx_client
        
        client = await jira_integration._get_client()
        
        assert client == mock_httpx_client
    
    def test_format_test_result_for_bug(self, jira_integration):
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
        
        description = jira_integration._format_test_result_for_bug(test_result)
        
        assert "Failing Test" in description
        assert "TestClass" in description
        assert "5.0s" in description
        assert "AssertionError" in description
        assert "at line 10" in description
        assert "smoke" in description
