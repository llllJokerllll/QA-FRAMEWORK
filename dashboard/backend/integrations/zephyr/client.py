"""
Zephyr Squad API Client

Implements IntegrationBase for Zephyr Squad (Jira plugin).
Zephyr uses Jira authentication and extends Jira with test management.

API Reference: https://support.smartbear.com/zephyr-squad-cloud/api-docs/
"""
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import httpx

from backend.integrations.base import IntegrationBase, TestResult, SyncResult, TestStatus
from backend.integrations.zephyr.config import ZephyrConfig


class ZephyrIntegration(IntegrationBase):
    """
    Zephyr Squad integration for test management in Jira.
    
    Features:
    - Test case management
    - Test cycles/executions
    - Import JUnit XML results
    - BDD/Cucumber support
    - Test traceability
    
    Free Tier: Up to 10 users, unlimited tests
    """
    
    provider_name = "zephyr"
    provider_display_name = "Zephyr Squad"
    provider_description = "Test management for Jira by Smart Bear"
    requires_auth = True
    supports_sync = True
    supports_test_cases = True
    supports_bugs = True
    supports_cycles = True  # Zephyr supports test cycles
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Parse config
        self.zephyr_config = ZephyrConfig(**config) if isinstance(config, dict) else config
        
        # Connection settings (use Jira credentials)
        self.base_url = self.zephyr_config.jira_base_url
        self.email = self.zephyr_config.jira_email
        self.api_token = self.zephyr_config.jira_api_token
        
        # Zephyr API base (different from Jira REST API)
        self.zephyr_api_base = f"{self.base_url}/rest/zapi/latest"
        
        # HTTP client
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.auth = (self.email, self.api_token)
        self._client: Optional[httpx.AsyncClient] = None
        self._project_id_cache: Dict[str, str] = {}
    
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
    
    async def _get_project_id(self, project_key: str) -> str:
        """Get project ID from key (cached)"""
        if project_key in self._project_id_cache:
            return self._project_id_cache[project_key]
        
        client = await self._get_client()
        response = await client.get(f'/rest/api/3/project/{project_key}')
        
        if response.status_code == 200:
            project_id = response.json().get('id')
            self._project_id_cache[project_key] = project_id
            return project_id
        
        raise Exception(f"Project not found: {project_key}")
    
    # ==================== Connection Methods ====================
    
    async def connect(self) -> bool:
        """Connect to Zephyr (via Jira)"""
        try:
            client = await self._get_client()
            response = await client.get('/rest/api/3/myself')
            
            if response.status_code == 200:
                # Also check Zephyr is installed
                zephyr_response = await client.get('/rest/zapi/latest/server-info')
                if zephyr_response.status_code == 200:
                    self.is_connected = True
                    return True
                else:
                    self._set_error("Zephyr Squad not installed in Jira")
                    return False
            else:
                self._set_error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self._set_error(f"Connection error: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Zephyr"""
        if self._client:
            await self._client.aclose()
            self._client = None
        self.is_connected = False
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Zephyr connection health"""
        start_time = time.time()
        
        if not self.is_connected:
            await self.connect()
        
        try:
            client = await self._get_client()
            
            # Check Jira
            jira_response = await client.get('/rest/api/3/myself')
            
            # Check Zephyr
            zephyr_response = await client.get('/rest/zapi/latest/server-info')
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            if jira_response.status_code == 200 and zephyr_response.status_code == 200:
                user = jira_response.json()
                zephyr_info = zephyr_response.json()
                
                return {
                    "status": "healthy",
                    "connected": True,
                    "latency_ms": latency_ms,
                    "server": self.base_url,
                    "user": user.get('displayName'),
                    "zephyr_version": zephyr_info.get('version'),
                    "error": None
                }
            else:
                return {
                    "status": "unhealthy",
                    "connected": False,
                    "latency_ms": latency_ms,
                    "error": "Zephyr or Jira not responding"
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
        """Sync test results to Zephyr test cycle"""
        if not self.is_connected:
            await self.connect()
        
        project = project_key or self.zephyr_config.default_project
        if not project:
            return SyncResult(
                provider=self.provider_name,
                success=False,
                errors=["No project key specified"]
            )
        
        # Create or get test cycle
        cycle_naming = cycle_name or self.zephyr_config.cycle_naming.format(
            date=datetime.now().strftime('%Y-%m-%d'),
            branch=kwargs.get('branch', 'main'),
            commit=kwargs.get('commit', '')[:8]
        )
        
        try:
            cycle = await self.create_test_cycle(
                name=cycle_naming,
                project_key=project,
                description=f"Automated test run from QA-FRAMEWORK"
            )
            cycle_id = cycle.get('id')
        except Exception as e:
            return SyncResult(
                provider=self.provider_name,
                success=False,
                errors=[f"Failed to create test cycle: {str(e)}"]
            )
        
        synced = 0
        failed = 0
        errors = []
        project_id = await self._get_project_id(project)
        
        for result in results:
            try:
                # Get or create test case
                test_case_key = result.issue_key
                if not test_case_key:
                    test_case = await self.create_test_case(
                        name=result.test_name,
                        description=f"Auto-generated from {result.classname or 'test suite'}",
                        project_key=project
                    )
                    test_case_key = test_case.get('key')
                
                # Get issue ID
                client = await self._get_client()
                issue_response = await client.get(f'/rest/api/3/issue/{test_case_key}')
                if issue_response.status_code != 200:
                    raise Exception(f"Issue not found: {test_case_key}")
                
                issue_id = issue_response.json().get('id')
                
                # Create execution record
                execution_payload = {
                    "issueId": issue_id,
                    "projectId": project_id,
                    "cycleId": cycle_id,
                    "status": self._map_status_to_zephyr(result.status)
                }
                
                exec_response = await client.post(
                    '/rest/zapi/latest/execution',
                    json=execution_payload
                )
                
                if exec_response.status_code == 200:
                    # Update execution with details
                    exec_id = list(exec_response.json().keys())[0]
                    
                    await client.put(
                        f'/rest/zapi/latest/execution/{exec_id}',
                        json={
                            "status": self._map_status_to_zephyr(result.status),
                            "comment": f"Duration: {result.duration}s\n{result.error or ''}"
                        }
                    )
                    synced += 1
                else:
                    failed += 1
                    errors.append(f"{result.test_name}: Failed to create execution")
                    
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
                "cycle_id": cycle_id,
                "cycle_name": cycle_naming,
                "cycle_url": f"{self.base_url}/browse/{project}?selectedItem=zephyr-test-cycles"
            }
        )
    
    def _map_status_to_zephyr(self, status: TestStatus) -> int:
        """Map test status to Zephyr status codes"""
        mapping = {
            TestStatus.PASSED: 1,
            TestStatus.FAILED: 2,
            TestStatus.SKIPPED: 3,
            TestStatus.BLOCKED: 4,
            TestStatus.UNTESTED: -1
        }
        return mapping.get(status, 2)
    
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
        """Create a test case in Zephyr (as Jira issue with Test type)"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": name,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }]
                },
                "issuetype": {"name": "Test"}  # Zephyr test case issue type
            }
        }
        
        if labels:
            payload["fields"]["labels"] = labels
        
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
        """Get test cases from Zephyr"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        project_id = await self._get_project_id(project_key)
        
        # Use Zephyr API to get tests
        response = await client.get(
            '/rest/zapi/latest/zql',
            params={
                'zqlQuery': f'project = "{project_key}" AND issueType = "Test"'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "id": issue.get("id"),
                    "key": issue.get("key"),
                    "name": issue.get("summary"),
                    "status": issue.get("executionStatus"),
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
        """Update a test case"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        
        fields = {}
        if updates.get('name'):
            fields['summary'] = updates['name']
        if updates.get('description'):
            fields['description'] = {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": updates['description']}]
                }]
            }
        
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
        """Create a bug in Jira (linked to test)"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }]
                },
                "issuetype": {"name": "Bug"},
                "priority": {"name": priority or "Medium"}
            }
        }
        
        if labels:
            payload["fields"]["labels"] = labels
        
        if test_result:
            payload["fields"]["labels"] = payload["fields"].get("labels", []) + [
                "auto-generated",
                f"test-{test_result.test_id}"
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
        
        jql = f'project = {project_key} AND issuetype = Bug'
        if status:
            jql += f' AND status = "{status}"'
        
        response = await client.post(
            '/rest/api/3/search',
            json={"jql": jql, "maxResults": 100}
        )
        
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "id": issue.get("id"),
                    "key": issue.get("key"),
                    "title": issue.get("fields", {}).get("summary"),
                    "status": issue.get("fields", {}).get("status", {}).get("name"),
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
    
    # ==================== Test Cycle Methods ====================
    
    async def create_test_cycle(
        self,
        name: str,
        project_key: str,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a test cycle in Zephyr"""
        if not self.is_connected:
            await self.connect()
        
        client = await self._get_client()
        project_id = await self._get_project_id(project_key)
        
        payload = {
            "name": name,
            "projectId": project_id,
            "description": description or f"Test cycle created {datetime.now().isoformat()}",
            "startDate": datetime.now().strftime('%d/%m/%Y'),
            "endDate": datetime.now().strftime('%d/%m/%Y')
        }
        
        response = await client.post('/rest/zapi/latest/cycle', json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "id": data.get("id"),
                "name": name,
                "project_key": project_key,
                "url": f"{self.base_url}/browse/{project_key}?selectedItem=zephyr-test-cycles"
            }
        else:
            raise Exception(f"Failed to create cycle: {response.text}")
    
    # ==================== Configuration ====================
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """Validate Zephyr configuration"""
        errors = []
        
        try:
            config = ZephyrConfig(**self.config)
        except Exception as e:
            errors.append(str(e))
            return False, errors
        
        if not config.jira_base_url:
            errors.append("jira_base_url is required")
        elif not config.jira_base_url.startswith('https://'):
            errors.append("jira_base_url must use HTTPS")
        
        if not config.jira_email:
            errors.append("jira_email is required")
        
        if not config.jira_api_token:
            errors.append("jira_api_token is required")
        
        return len(errors) == 0, errors
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for UI"""
        return {
            "type": "object",
            "title": "Zephyr Squad Configuration",
            "properties": {
                "jira_base_url": {
                    "type": "string",
                    "title": "Jira URL",
                    "description": "Jira instance where Zephyr is installed",
                    "format": "uri"
                },
                "jira_email": {
                    "type": "string",
                    "title": "Jira Email",
                    "format": "email"
                },
                "jira_api_token": {
                    "type": "string",
                    "title": "Jira API Token",
                    "secret": True
                },
                "default_project": {
                    "type": "string",
                    "title": "Default Project Key"
                },
                "auto_create_cycles": {
                    "type": "boolean",
                    "title": "Auto-create Test Cycles",
                    "default": True
                },
                "cycle_naming": {
                    "type": "string",
                    "title": "Cycle Name Template",
                    "description": "Variables: {date}, {branch}, {commit}",
                    "default": "CI Run {date}"
                }
            },
            "required": ["jira_base_url", "jira_email", "jira_api_token"]
        }
