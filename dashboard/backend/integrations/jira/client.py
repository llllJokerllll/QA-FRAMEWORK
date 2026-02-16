"""
Jira API Client

Implements IntegrationBase for Atlassian Jira.
Supports both Jira Cloud and Jira Server (on-premise).

API Reference:
- Jira Cloud: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- Jira Server: https://docs.atlassian.com/software/jira/docs/api/REST/8.13.0/
"""
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import httpx

from backend.integrations.base import IntegrationBase, TestResult, SyncResult, TestStatus
from backend.integrations.jira.config import JiraConfig


class JiraIntegration(IntegrationBase):
    """
    Jira integration for test management.
    
    Features:
    - Create bugs from failed tests
    - Sync test results as issues
    - Link tests to epics/stories
    - Add comments to issues
    - Transition issue status
    
    Free Tier: Up to 10 users
    """
    
    provider_name = "jira"
    provider_display_name = "Jira (Atlassian)"
    provider_description = "Atlassian Jira issue tracking and project management"
    requires_auth = True
    supports_sync = True
    supports_test_cases = True
    supports_bugs = True
    supports_cycles = False
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Parse config
        self.jira_config = JiraConfig(**config) if isinstance(config, dict) else config
        
        # Connection settings
        self.base_url = self.jira_config.base_url
        self.email = self.jira_config.email
        self.api_token = self.jira_config.api_token
        
        # HTTP client
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.auth = (self.email, self.api_token)
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                auth=self.auth,
                timeout=30.0,
                follow_redirects=True
            )
        return self._client
    
    # ==================== Connection Methods ====================
    
    async def connect(self) -> bool:
        """Connect to Jira and validate credentials"""
        try:
            client = await self._get_client()
            response = await client.get('/rest/api/3/myself')
            
            if response.status_code == 200:
                self.is_connected = True
                self._current_user = response.json()
                return True
            else:
                self._set_error(f"Authentication failed: {response.status_code}")
                self.is_connected = False
                return False
                
        except Exception as e:
            self._set_error(f"Connection error: {str(e)}")
            self.is_connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Jira"""
        if self._client:
            await self._client.aclose()
            self._client = None
        self.is_connected = False
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Jira connection health"""
        start_time = time.time()
        
        if not self.is_connected:
            await self.connect()
        
        try:
            client = await self._get_client()
            response = await client.get('/rest/api/3/myself')
            latency_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                user = response.json()
                return {
                    "status": "healthy",
                    "connected": True,
                    "latency_ms": latency_ms,
                    "server": self.base_url,
                    "user": user.get('displayName'),
                    "account_id": user.get('accountId'),
                    "error": None
                }
            else:
                return {
                    "status": "unhealthy",
                    "connected": False,
                    "latency_ms": latency_ms,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "latency_ms": int((time.time() - start_time) * 1000),
                "error": str(e)
            }
    
    # ==================== Synchronization Methods ====================
    
    async def sync_test_results(
        self,
        results: List[TestResult],
        project_key: Optional[str] = None,
        cycle_name: Optional[str] = None,
        **kwargs
    ) -> SyncResult:
        """
        Sync test results to Jira.
        
        For failed tests: Creates bugs
        For passed tests: Optionally adds comments to linked issues
        """
        if not self.is_connected:
            await self.connect()
        
        project = project_key or self.jira_config.default_project
        if not project:
            return SyncResult(
                provider=self.provider_name,
                success=False,
                errors=["No project key specified"]
            )
        
        synced = 0
        failed = 0
        errors = []
        created_bugs = []
        
        for result in results:
            try:
                if result.status == TestStatus.FAILED and self.jira_config.auto_create_bugs:
                    # Create bug for failed test
                    bug = await self.create_bug(
                        title=f"[QA] Test Failed: {result.test_name}",
                        description=self._format_test_result_for_bug(result),
                        project_key=project,
                        test_result=result,
                        labels=[self.jira_config.label_prefix, "auto-generated"]
                    )
                    created_bugs.append(bug)
                    synced += 1
                    
                elif result.issue_key:
                    # Add comment to existing issue
                    await self.add_comment(
                        issue_key=result.issue_key,
                        comment=f"✅ Test passed automatically\n\nDuration: {result.duration}s"
                    )
                    synced += 1
                    
                else:
                    synced += 1  # Count as synced even if no action needed
                    
            except Exception as e:
                failed += 1
                errors.append(f"{result.test_name}: {str(e)}")
        
        return SyncResult(
            provider=self.provider_name,
            success=(failed == 0),
            synced_count=synced,
            failed_count=failed,
            errors=errors,
            details={
                "created_bugs": len(created_bugs),
                "bugs": created_bugs
            }
        )
    
    # ==================== Test Case Methods ====================
    
    async def create_test_case(
        self,
        name: str,
        description: str,
        project_key: str,
        folder: Optional[str] = None,
        labels: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a test case as a Jira issue"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        
        # Build issue payload
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": name,
                "description": self._build_description(description),
                "issuetype": {"name": kwargs.get('issue_type', self.jira_config.default_test_issue_type)}
            }
        }
        
        if labels:
            payload["fields"]["labels"] = labels
        
        if folder:
            # Add folder as a label or custom field
            payload["fields"]["labels"] = payload["fields"].get("labels", []) + [f"folder:{folder}"]
        
        response = await client.post('/rest/api/3/issue', json=payload)
        
        if response.status_code == 201:
            data = response.json()
            return {
                "id": data.get("id"),
                "key": data.get("key"),
                "name": name,
                "url": f"{self.base_url}/browse/{data.get('key')}"
            }
        else:
            raise Exception(f"Failed to create test case: {response.text}")
    
    async def get_test_cases(
        self,
        project_key: str,
        folder: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get test cases from Jira"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        
        # Build JQL query
        jql = f'project = {project_key}'
        
        if filters:
            if filters.get('issue_type'):
                jql += f' AND issuetype = "{filters["issue_type"]}"'
            if filters.get('status'):
                jql += f' AND status = "{filters["status"]}"'
            if filters.get('labels'):
                for label in filters['labels']:
                    jql += f' AND labels = "{label}"'
        
        if folder:
            jql += f' AND labels = "folder:{folder}"'
        
        response = await client.post(
            '/rest/api/3/search',
            json={"jql": jql, "maxResults": 100, "fields": ["summary", "status", "labels", "issuetype"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "id": issue.get("id"),
                    "key": issue.get("key"),
                    "name": issue.get("fields", {}).get("summary"),
                    "status": issue.get("fields", {}).get("status", {}).get("name"),
                    "labels": issue.get("fields", {}).get("labels", []),
                    "url": f"{self.base_url}/browse/{issue.get('key')}"
                }
                for issue in data.get("issues", [])
            ]
        
        return []
    
    async def update_test_case(
        self,
        test_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a test case in Jira"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        
        # Build update payload
        fields = {}
        if updates.get('name'):
            fields['summary'] = updates['name']
        if updates.get('description'):
            fields['description'] = self._build_description(updates['description'])
        if updates.get('labels'):
            fields['labels'] = updates['labels']
        
        response = await client.put(f'/rest/api/3/issue/{test_id}', json={"fields": fields})
        
        if response.status_code == 204:
            return {"id": test_id, "updated": True}
        else:
            raise Exception(f"Failed to update test case: {response.text}")
    
    # ==================== Bug Methods ====================
    
    async def create_bug(
        self,
        title: str,
        description: str,
        project_key: str,
        test_result: Optional[TestResult] = None,
        severity: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a bug in Jira"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        
        # Build issue payload
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": title,
                "description": self._build_description(description),
                "issuetype": {"name": self.jira_config.default_issue_type}
            }
        }
        
        if priority:
            payload["fields"]["priority"] = {"name": priority}
        else:
            payload["fields"]["priority"] = {"name": "Medium"}
        
        if labels:
            payload["fields"]["labels"] = labels
        
        # Add QA-specific labels
        payload["fields"]["labels"] = payload["fields"].get("labels", []) + [
            self.jira_config.label_prefix,
            f"test-{test_result.test_id}" if test_result else ""
        ]
        
        response = await client.post('/rest/api/3/issue', json=payload)
        
        if response.status_code == 201:
            data = response.json()
            return {
                "id": data.get("id"),
                "key": data.get("key"),
                "url": f"{self.base_url}/browse/{data.get('key')}"
            }
        else:
            raise Exception(f"Failed to create bug: {response.text}")
    
    async def get_bugs(
        self,
        project_key: str,
        status: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get bugs from Jira"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        
        # Build JQL query
        jql = f'project = {project_key} AND issuetype = "{self.jira_config.default_issue_type}"'
        
        if status:
            jql += f' AND status = "{status}"'
        
        if filters:
            if filters.get('labels'):
                for label in filters['labels']:
                    jql += f' AND labels = "{label}"'
        
        response = await client.post(
            '/rest/api/3/search',
            json={"jql": jql, "maxResults": 100, "fields": ["summary", "status", "priority", "labels"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "id": issue.get("id"),
                    "key": issue.get("key"),
                    "title": issue.get("fields", {}).get("summary"),
                    "status": issue.get("fields", {}).get("status", {}).get("name"),
                    "priority": issue.get("fields", {}).get("priority", {}).get("name"),
                    "url": f"{self.base_url}/browse/{issue.get('key')}"
                }
                for issue in data.get("issues", [])
            ]
        
        return []
    
    # ==================== Project Methods ====================
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of Jira projects"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        response = await client.get('/rest/api/3/project')
        
        if response.status_code == 200:
            projects = response.json()
            return [
                {
                    "key": p.get("key"),
                    "name": p.get("name"),
                    "id": p.get("id")
                }
                for p in projects
            ]
        
        return []
    
    # ==================== Additional Jira Methods ====================
    
    async def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to an issue"""
        client = await self._get_client()
        
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}]
                    }
                ]
            }
        }
        
        response = await client.post(f'/rest/api/3/issue/{issue_key}/comment', json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to add comment: {response.text}")
    
    async def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        """Transition an issue to a new status"""
        client = await self._get_client()
        
        response = await client.post(
            f'/rest/api/3/issue/{issue_key}/transitions',
            json={"transition": {"id": transition_id}}
        )
        
        return response.status_code == 204
    
    async def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get available transitions for an issue"""
        client = await self._get_client()
        
        response = await client.get(f'/rest/api/3/issue/{issue_key}/transitions')
        
        if response.status_code == 200:
            data = response.json()
            return data.get("transitions", [])
        
        return []
    
    # ==================== Configuration ====================
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """Validate Jira configuration"""
        errors = []
        
        try:
            config = JiraConfig(**self.config)
        except Exception as e:
            errors.append(str(e))
            return False, errors
        
        if not config.base_url:
            errors.append("base_url is required")
        elif not config.base_url.startswith('https://'):
            errors.append("base_url must use HTTPS")
        
        if not config.email:
            errors.append("email is required")
        elif '@' not in config.email:
            errors.append("Invalid email format")
        
        if not config.api_token:
            errors.append("api_token is required")
        
        return len(errors) == 0, errors
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for UI"""
        return {
            "type": "object",
            "title": "Jira Configuration",
            "properties": {
                "base_url": {
                    "type": "string",
                    "title": "Jira URL",
                    "description": "Your Jira instance URL",
                    "placeholder": "https://yourcompany.atlassian.net",
                    "format": "uri"
                },
                "email": {
                    "type": "string",
                    "title": "Email",
                    "description": "Your Jira account email",
                    "format": "email"
                },
                "api_token": {
                    "type": "string",
                    "title": "API Token",
                    "description": "Generate at: Atlassian Account Settings > Security > API tokens",
                    "secret": True
                },
                "default_project": {
                    "type": "string",
                    "title": "Default Project Key",
                    "description": "Default project for test cases and bugs"
                },
                "default_issue_type": {
                    "type": "string",
                    "title": "Default Issue Type",
                    "description": "Issue type for bugs",
                    "default": "Bug",
                    "enum": ["Bug", "Task", "Story", "Improvement"]
                },
                "auto_create_bugs": {
                    "type": "boolean",
                    "title": "Auto-create Bugs",
                    "description": "Automatically create bugs for failed tests",
                    "default": True
                },
                "label_prefix": {
                    "type": "string",
                    "title": "Label Prefix",
                    "description": "Prefix for labels added to issues",
                    "default": "qa-framework"
                }
            },
            "required": ["base_url", "email", "api_token"]
        }
    
    # ==================== Helpers ====================
    
    def _build_description(self, text: str) -> Dict[str, Any]:
        """Build Atlassian Document Format description"""
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text}]
                }
            ]
        }
