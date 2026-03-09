"""
AI Root Cause Analyzer

Analyzes test failures and suggests root causes:
- Pattern analysis
- Error clustering
- Fix suggestions
- Historical correlation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class RootCauseAnalyzer:
    """AI-powered root cause analysis"""
    
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
    
    async def analyze_failure(
        self,
        test_name: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        test_code: Optional[str] = None,
        execution_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Analyze test failure and identify root cause
        
        Args:
            test_name: Name of failed test
            error_message: Error message
            stack_trace: Stack trace (optional)
            test_code: Test code (optional)
            execution_history: Previous executions (optional)
        
        Returns:
            Root cause analysis with suggestions
        """
        
        # Pattern analysis
        patterns = self._identify_patterns(error_message, stack_trace)
        
        # Error clustering
        cluster = self._cluster_error(error_message)
        
        # Generate analysis
        analysis = {
            "test_name": test_name,
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": cluster["type"],
            "patterns": patterns,
            "root_cause": await self._generate_root_cause_hypothesis(
                test_name, error_message, patterns, execution_history
            ),
            "suggested_fixes": await self._generate_fix_suggestions(
                test_name, error_message, patterns, test_code
            ),
            "confidence": self._calculate_confidence(patterns, execution_history),
            "related_failures": []
        }
        
        logger.info(
            "Root cause analysis completed",
            test_name=test_name,
            error_type=cluster["type"],
            confidence=analysis["confidence"]
        )
        
        return analysis
    
    def _identify_patterns(
        self,
        error_message: str,
        stack_trace: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Identify patterns in error"""
        
        patterns = []
        
        # Common error patterns
        error_patterns = {
            "assertion_failed": ["AssertionError", "assert", "expected"],
            "timeout": ["TimeoutError", "timed out", "timeout"],
            "element_not_found": ["NoSuchElement", "not found", "Unable to locate"],
            "connection_refused": ["ConnectionRefused", "connection refused", "ECONNREFUSED"],
            "null_pointer": ["NullPointerException", "NoneType", "undefined"],
            "permission_denied": ["PermissionDenied", "403", "Forbidden"],
            "not_found": ["404", "Not Found", "does not exist"],
            "rate_limit": ["RateLimitExceeded", "429", "Too Many Requests"]
        }
        
        for pattern_type, keywords in error_patterns.items():
            if any(keyword in error_message for keyword in keywords):
                patterns.append({
                    "type": pattern_type,
                    "keywords": [k for k in keywords if k in error_message],
                    "severity": "high" if pattern_type in ["assertion_failed", "timeout"] else "medium"
                })
        
        # Stack trace patterns
        if stack_trace:
            if "File" in stack_trace and "line" in stack_trace:
                patterns.append({
                    "type": "file_location",
                    "severity": "info"
                })
        
        return patterns
    
    def _cluster_error(self, error_message: str) -> Dict[str, str]:
        """Cluster error into category"""
        
        error_types = {
            "assertion": ["assert", "expected", "should"],
            "timeout": ["timeout", "timed out"],
            "network": ["connection", "network", "ECONNREFUSED", "ETIMEDOUT"],
            "element": ["element", "selector", "not found", "locate"],
            "data": ["data", "null", "undefined", "NoneType"],
            "permission": ["permission", "403", "forbidden"],
            "resource": ["404", "not found", "does not exist"]
        }
        
        for error_type, keywords in error_types.items():
            if any(keyword.lower() in error_message.lower() for keyword in keywords):
                return {"type": error_type, "category": "test_failure"}
        
        return {"type": "unknown", "category": "test_failure"}
    
    async def _generate_root_cause_hypothesis(
        self,
        test_name: str,
        error_message: str,
        patterns: List[Dict],
        execution_history: Optional[List[Dict]]
    ) -> str:
        """Generate root cause hypothesis"""
        
        # Simple rule-based analysis (would use LLM in production)
        if any(p["type"] == "timeout" for p in patterns):
            return "Test execution exceeded timeout limit. Possible causes: slow network, resource contention, or infinite loop."
        
        if any(p["type"] == "element_not_found" for p in patterns):
            return "UI element not found. Possible causes: selector changed, element not loaded, or timing issue."
        
        if any(p["type"] == "assertion_failed" for p in patterns):
            return "Assertion failed. Possible causes: business logic error, test data issue, or environment difference."
        
        if any(p["type"] == "connection_refused" for p in patterns):
            return "Connection refused. Possible causes: service down, wrong port/host, or firewall blocking."
        
        return "Unknown root cause. Manual investigation required."
    
    async def _generate_fix_suggestions(
        self,
        test_name: str,
        error_message: str,
        patterns: List[Dict],
        test_code: Optional[str]
    ) -> List[Dict[str, str]]:
        """Generate fix suggestions"""
        
        suggestions = []
        
        if any(p["type"] == "timeout" for p in patterns):
            suggestions.append({
                "type": "increase_timeout",
                "description": "Increase test timeout",
                "code": "timeout = 60  # Increase from 30s to 60s",
                "confidence": "high"
            })
            suggestions.append({
                "type": "add_wait",
                "description": "Add explicit wait for slow elements",
                "code": "await page.waitForSelector('.slow-element', timeout=10000)",
                "confidence": "medium"
            })
        
        if any(p["type"] == "element_not_found" for p in patterns):
            suggestions.append({
                "type": "update_selector",
                "description": "Update selector to match current UI",
                "code": "selector = '[data-testid=\"new-button\"]'  # Updated selector",
                "confidence": "high"
            })
            suggestions.append({
                "type": "add_wait",
                "description": "Wait for element to load",
                "code": "await page.waitForSelector('#element', visible=True)",
                "confidence": "medium"
            })
        
        if any(p["type"] == "assertion_failed" for p in patterns):
            suggestions.append({
                "type": "update_assertion",
                "description": "Update assertion to match expected behavior",
                "code": "assert result.status == 'success'  # Updated expected value",
                "confidence": "medium"
            })
            suggestions.append({
                "type": "check_test_data",
                "description": "Verify test data is correct",
                "code": "# Ensure test user exists in database",
                "confidence": "low"
            })
        
        return suggestions
    
    def _calculate_confidence(
        self,
        patterns: List[Dict],
        execution_history: Optional[List[Dict]]
    ) -> float:
        """Calculate confidence score"""
        
        base_confidence = 0.5
        
        # More patterns = higher confidence
        base_confidence += min(len(patterns) * 0.1, 0.3)
        
        # Historical data = higher confidence
        if execution_history and len(execution_history) > 0:
            base_confidence += 0.2
        
        return min(base_confidence, 0.95)
    
    async def batch_analyze(
        self,
        failures: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze multiple failures for patterns"""
        
        analyses = []
        error_types = {}
        
        for failure in failures:
            analysis = await self.analyze_failure(
                test_name=failure.get("test_name"),
                error_message=failure.get("error_message"),
                stack_trace=failure.get("stack_trace")
            )
            analyses.append(analysis)
            
            # Track error types
            error_type = analysis["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Find most common root causes
        common_causes = sorted(
            error_types.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_failures": len(failures),
            "analyses": analyses,
            "common_causes": common_causes,
            "recommendation": await self._generate_batch_recommendation(common_causes)
        }
    
    async def _generate_batch_recommendation(
        self,
        common_causes: List[tuple]
    ) -> str:
        """Generate recommendation for batch failures"""
        
        if not common_causes:
            return "No failures to analyze."
        
        top_cause, count = common_causes[0]
        
        return f"Most common failure: {top_cause} ({count} occurrences). Focus on fixing this category first."
