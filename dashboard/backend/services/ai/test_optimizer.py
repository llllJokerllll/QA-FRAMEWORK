"""
AI Test Optimizer

Suggests test optimizations:
- Detect redundant tests
- Suggest parallelization
- Optimize selectors
- Reduce flakiness
"""

from typing import List, Dict, Any
import structlog

logger = structlog.get_logger()


class TestOptimizer:
    """AI-powered test optimization"""
    
    def __init__(self):
        pass
    
    async def analyze_suite(
        self,
        test_cases: List[Dict[str, Any]],
        execution_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze test suite and suggest optimizations
        
        Args:
            test_cases: List of test cases
            execution_history: Historical execution data
        
        Returns:
            Optimization suggestions
        """
        
        suggestions = []
        
        # Detect redundant tests
        redundant = await self._detect_redundant_tests(test_cases)
        if redundant:
            suggestions.append({
                "type": "redundant_tests",
                "severity": "medium",
                "description": f"Found {len(redundant)} potentially redundant tests",
                "tests": redundant,
                "recommendation": "Consider removing or consolidating duplicate tests"
            })
        
        # Suggest parallelization
        parallelizable = await self._identify_parallelizable_tests(test_cases)
        if parallelizable:
            suggestions.append({
                "type": "parallelization",
                "severity": "high",
                "description": f"{len(parallelizable)} tests can be run in parallel",
                "tests": parallelizable,
                "recommendation": "Enable parallel execution to reduce total runtime"
            })
        
        # Detect flaky tests
        flaky = await self._detect_flaky_tests(execution_history)
        if flaky:
            suggestions.append({
                "type": "flaky_tests",
                "severity": "high",
                "description": f"Found {len(flaky)} flaky tests",
                "tests": flaky,
                "recommendation": "Investigate and fix flaky tests"
            })
        
        # Optimize selectors
        selector_improvements = await self._suggest_selector_improvements(test_cases)
        if selector_improvements:
            suggestions.append({
                "type": "selector_optimization",
                "severity": "medium",
                "description": "Selectors can be improved",
                "improvements": selector_improvements,
                "recommendation": "Update selectors for better reliability"
            })
        
        # Calculate potential time savings
        time_savings = self._calculate_time_savings(suggestions, execution_history)
        
        return {
            "total_tests": len(test_cases),
            "suggestions": suggestions,
            "potential_time_savings": time_savings,
            "optimization_score": self._calculate_optimization_score(suggestions)
        }
    
    async def _detect_redundant_tests(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect potentially redundant tests"""
        
        redundant = []
        seen_signatures = {}
        
        for test in test_cases:
            # Create signature from test code
            code = test.get("test_code", "")
            signature = self._create_code_signature(code)
            
            if signature in seen_signatures:
                redundant.append({
                    "test_id": test.get("id"),
                    "test_name": test.get("name"),
                    "duplicate_of": seen_signatures[signature],
                    "similarity": 0.95
                })
            else:
                seen_signatures[signature] = test.get("name")
        
        return redundant
    
    def _create_code_signature(self, code: str) -> str:
        """Create signature from code (normalize whitespace, remove comments)"""
        
        # Simple normalization (would be more sophisticated in production)
        lines = []
        for line in code.split("\n"):
            # Remove comments
            if "#" in line:
                line = line[:line.index("#")]
            # Normalize whitespace
            line = " ".join(line.split())
            if line:
                lines.append(line)
        
        return "\n".join(lines)
    
    async def _identify_parallelizable_tests(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify tests that can run in parallel"""
        
        parallelizable = []
        
        for test in test_cases:
            code = test.get("test_code", "")
            
            # Check for parallelization blockers
            blockers = [
                "time.sleep",
                "global_state",
                "singleton",
                "shared_resource",
                "database.transaction"
            ]
            
            has_blockers = any(blocker in code for blocker in blockers)
            
            if not has_blockers:
                parallelizable.append(test.get("name"))
        
        return parallelizable
    
    async def _detect_flaky_tests(
        self,
        execution_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect flaky tests from execution history"""
        
        if not execution_history:
            return []
        
        # Group by test name
        test_results = {}
        for execution in execution_history:
            for result in execution.get("results", []):
                test_name = result.get("test_name")
                if test_name not in test_results:
                    test_results[test_name] = []
                test_results[test_name].append(result.get("status"))
        
        # Identify flaky (pass rate between 0.3 and 0.95)
        flaky = []
        for test_name, results in test_results.items():
            if len(results) >= 3:  # Need at least 3 runs
                pass_rate = results.count("passed") / len(results)
                if 0.3 <= pass_rate <= 0.95:
                    flaky.append({
                        "test_name": test_name,
                        "pass_rate": pass_rate,
                        "runs": len(results),
                        "flakiness_score": 1 - abs(pass_rate - 0.5) * 2
                    })
        
        return sorted(flaky, key=lambda x: x["flakiness_score"], reverse=True)
    
    async def _suggest_selector_improvements(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Suggest selector improvements"""
        
        improvements = []
        
        bad_patterns = [
            ("//*[@id='", "Use CSS selectors instead of complex XPath"),
            ("//div[", "Avoid fragile DOM structure selectors"),
            (":nth-child", "Use data-testid attributes instead of positional selectors"),
            ("[class='", "Use specific data attributes instead of generic classes")
        ]
        
        for test in test_cases:
            code = test.get("test_code", "")
            
            for pattern, suggestion in bad_patterns:
                if pattern in code:
                    improvements.append({
                        "test_name": test.get("name"),
                        "current_pattern": pattern,
                        "suggestion": suggestion,
                        "severity": "medium"
                    })
        
        return improvements
    
    def _calculate_time_savings(
        self,
        suggestions: List[Dict],
        execution_history: List[Dict]
    ) -> Dict[str, float]:
        """Calculate potential time savings"""
        
        if not execution_history:
            return {"hours_per_week": 0, "percentage": 0}
        
        # Estimate based on suggestions
        avg_duration = sum(e.get("duration", 0) for e in execution_history) / len(execution_history)
        
        savings_multiplier = 0
        
        for suggestion in suggestions:
            if suggestion["type"] == "parallelization":
                savings_multiplier += 0.4  # 40% time savings
            elif suggestion["type"] == "redundant_tests":
                savings_multiplier += 0.15  # 15% time savings
            elif suggestion["type"] == "flaky_tests":
                savings_multiplier += 0.1  # 10% time savings (less re-runs)
        
        # Estimate weekly savings (assume 5 executions per week)
        weekly_executions = 5
        current_weekly_time = avg_duration * weekly_executions
        potential_savings = current_weekly_time * savings_multiplier
        
        return {
            "hours_per_week": round(potential_savings / 3600, 1),
            "percentage": round(savings_multiplier * 100, 1)
        }
    
    def _calculate_optimization_score(self, suggestions: List[Dict]) -> float:
        """Calculate overall optimization score (0-100)"""
        
        if not suggestions:
            return 100.0  # Already optimized
        
        # Start from 100 and subtract for each issue
        score = 100.0
        
        for suggestion in suggestions:
            severity = suggestion.get("severity", "low")
            
            if severity == "high":
                score -= 20
            elif severity == "medium":
                score -= 10
            else:
                score -= 5
        
        return max(score, 0.0)
