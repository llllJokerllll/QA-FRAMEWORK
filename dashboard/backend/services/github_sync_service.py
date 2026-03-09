"""
GitHub Sync Service

Bidirectional sync with GitHub:
- Import tests from repository
- Push results to PR comments
- Status checks on commits
- Sync with GitHub Actions
"""

import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class GitHubSyncService:
    """Service for GitHub integration"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def get_repository_info(
        self,
        owner: str,
        repo: str
    ) -> Dict[str, Any]:
        """Get repository information"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def list_test_files(
        self,
        owner: str,
        repo: str,
        branch: str = "main"
    ) -> List[str]:
        """
        List test files in repository
        
        Looks for files matching patterns:
        - test_*.py
        - *_test.py
        - *.test.js
        - *.spec.ts
        """
        async with aiohttp.ClientSession() as session:
            # Get tree
            url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
            
            # Filter test files
            test_patterns = ["test_", "_test.py", ".test.js", ".spec.ts"]
            test_files = [
                file["path"]
                for file in data.get("tree", [])
                if file["type"] == "blob"
                and any(pattern in file["path"] for pattern in test_patterns)
            ]
            
            return test_files
    
    async def create_pr_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str
    ) -> Dict[str, Any]:
        """Create comment on pull request"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
            async with session.post(
                url,
                headers=self.headers,
                json={"body": body}
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def create_status_check(
        self,
        owner: str,
        repo: str,
        sha: str,
        state: str,
        description: str,
        context: str = "qa-framework/tests"
    ) -> Dict[str, Any]:
        """
        Create commit status check
        
        States: pending, success, failure, error
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/statuses/{sha}"
            async with session.post(
                url,
                headers=self.headers,
                json={
                    "state": state,
                    "description": description,
                    "context": context
                }
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def create_check_run(
        self,
        owner: str,
        repo: str,
        head_sha: str,
        name: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create GitHub Check Run
        
        Status: queued, in_progress, completed
        Conclusion: success, failure, neutral, cancelled, timed_out, action_required
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/check-runs"
            payload = {
                "name": name,
                "head_sha": head_sha,
                "status": status
            }
            
            if conclusion:
                payload["conclusion"] = conclusion
            
            if output:
                payload["output"] = output
            
            async with session.post(
                url,
                headers=self.headers,
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_pull_request_files(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get files changed in pull request"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def format_test_results_comment(
        self,
        suite_name: str,
        total_tests: int,
        passed: int,
        failed: int,
        duration: float,
        test_results: List[Dict[str, Any]]
    ) -> str:
        """Format test results as PR comment"""
        
        status_emoji = "✅" if failed == 0 else "❌"
        
        comment = f"""
## {status_emoji} QA-FRAMEWORK Test Results

**Suite:** {suite_name}
**Status:** {passed}/{total_tests} passed
**Duration:** {duration:.1f}s

| Test | Status | Duration |
|------|--------|----------|
"""
        
        for test in test_results[:10]:  # Limit to 10 tests
            emoji = "✅" if test["status"] == "passed" else "❌"
            comment += f"| {test['name']} | {emoji} {test['status']} | {test['duration']}s |\n"
        
        if len(test_results) > 10:
            comment += f"\n*...and {len(test_results) - 10} more tests*\n"
        
        comment += "\n---\n*Powered by [QA-FRAMEWORK](https://qa-framework.io)*"
        
        return comment


class GitHubWebhookHandler:
    """Handle GitHub webhooks"""
    
    def __init__(self, sync_service: GitHubSyncService):
        self.sync_service = sync_service
    
    async def handle_push_event(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle push event"""
        logger.info("Push event received", ref=payload.get("ref"))
        
        # Trigger test run on push
        # Would create test execution here
        
        return {"status": "processed", "event": "push"}
    
    async def handle_pull_request_event(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle pull request event"""
        action = payload.get("action")
        pr_number = payload.get("number")
        
        logger.info(
            "Pull request event received",
            action=action,
            pr_number=pr_number
        )
        
        if action in ["opened", "synchronize"]:
            # Create pending status check
            owner = payload["repository"]["owner"]["login"]
            repo = payload["repository"]["name"]
            sha = payload["pull_request"]["head"]["sha"]
            
            await self.sync_service.create_status_check(
                owner=owner,
                repo=repo,
                sha=sha,
                state="pending",
                description="Tests are running..."
            )
            
            # Trigger test run
        
        return {"status": "processed", "event": "pull_request"}
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """Verify GitHub webhook signature"""
        import hmac
        import hashlib
        
        expected = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)
