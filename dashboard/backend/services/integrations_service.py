"""
Slack & Discord Notification Services

Webhook-based notifications for Slack and Discord
"""

import aiohttp
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()


class SlackService:
    """Service for Slack notifications"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_message(
        self,
        text: str,
        blocks: Optional[List[Dict]] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """Send message to Slack"""
        payload = {"text": text}
        
        if blocks:
            payload["blocks"] = blocks
        
        if attachments:
            payload["attachments"] = attachments
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url,
                json=payload
            ) as response:
                if response.status == 200:
                    logger.info("Slack message sent")
                    return True
                else:
                    logger.error("Slack message failed", status=response.status)
                    return False
    
    async def send_test_result(
        self,
        suite_name: str,
        status: str,
        total: int,
        passed: int,
        failed: int,
        duration: float
    ):
        """Send test result notification"""
        
        color = "good" if failed == 0 else "danger"
        emoji = "✅" if failed == 0 else "❌"
        
        attachment = {
            "color": color,
            "title": f"{emoji} Test Suite: {suite_name}",
            "fields": [
                {"title": "Status", "value": status.upper(), "short": True},
                {"title": "Passed", "value": f"{passed}/{total}", "short": True},
                {"title": "Failed", "value": str(failed), "short": True},
                {"title": "Duration", "value": f"{duration:.1f}s", "short": True}
            ],
            "footer": "QA-FRAMEWORK",
            "footer_icon": "https://qa-framework.io/logo.png",
            "ts": int(datetime.now().timestamp())
        }
        
        await self.send_message(
            text=f"Test suite completed: {suite_name}",
            attachments=[attachment]
        )


class DiscordService:
    """Service for Discord notifications"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_message(
        self,
        content: str,
        embed: Optional[Dict] = None
    ) -> bool:
        """Send message to Discord"""
        payload = {"content": content}
        
        if embed:
            payload["embeds"] = [embed]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url,
                json=payload
            ) as response:
                if response.status in [200, 204]:
                    logger.info("Discord message sent")
                    return True
                else:
                    logger.error("Discord message failed", status=response.status)
                    return False
    
    async def send_test_result(
        self,
        suite_name: str,
        status: str,
        total: int,
        passed: int,
        failed: int,
        duration: float
    ):
        """Send test result notification"""
        
        color = 3066993 if failed == 0 else 15158332  # Green or Red
        emoji = "✅" if failed == 0 else "❌"
        
        embed = {
            "title": f"{emoji} Test Suite Completed",
            "description": f"**{suite_name}**",
            "color": color,
            "fields": [
                {"name": "Status", "value": status.upper(), "inline": True},
                {"name": "Results", "value": f"{passed}/{total} passed", "inline": True},
                {"name": "Failed", "value": str(failed), "inline": True},
                {"name": "Duration", "value": f"{duration:.1f}s", "inline": True}
            ],
            "footer": {"text": "QA-FRAMEWORK"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_message(
            content=f"Test results for {suite_name}",
            embed=embed
        )


class JiraService:
    """Service for Jira integration"""
    
    def __init__(self, base_url: str, api_token: str, email: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.email = email
        self.auth = aiohttp.BasicAuth(email, api_token)
    
    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Bug",
        priority: str = "Medium",
        labels: List[str] = None
    ) -> Dict[str, Any]:
        """Create Jira issue"""
        url = f"{self.base_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }
                    ]
                },
                "issuetype": {"name": issue_type},
                "priority": {"name": priority}
            }
        }
        
        if labels:
            payload["fields"]["labels"] = labels
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                auth=self.auth,
                json=payload,
                headers={"Accept": "application/json"}
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def create_bug_from_test_failure(
        self,
        project_key: str,
        test_name: str,
        error_message: str,
        execution_id: int
    ):
        """Create bug from failed test"""
        
        summary = f"Test Failure: {test_name}"
        description = f"""
Test: {test_name}
Execution ID: {execution_id}
Error: {error_message}

This issue was automatically created by QA-FRAMEWORK.
        """
        
        issue = await self.create_issue(
            project_key=project_key,
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="High",
            labels=["qa-framework", "automated"]
        )
        
        logger.info(
            "Jira issue created from test failure",
            issue_key=issue["key"],
            test_name=test_name
        )
        
        return issue
    
    async def add_comment(
        self,
        issue_key: str,
        comment: str
    ):
        """Add comment to Jira issue"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                auth=self.auth,
                json=payload,
                headers={"Accept": "application/json"}
            ) as response:
                response.raise_for_status()
                return await response.json()
