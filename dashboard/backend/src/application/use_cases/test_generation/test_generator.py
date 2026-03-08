"""
Test Generation Use Cases

Application-layer use cases for AI-powered test generation.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import uuid4
import logging

from src.domain.test_generation.entities import GeneratedTest, TestScenario, EdgeCase
from src.domain.test_generation.value_objects import (
    GenerationType,
    TestPriority,
    ConfidenceLevel,
    TestType,
    EdgeCaseType,
    TestStep,
    TestAssertion,
    TestData,
    GherkinScenario,
    TestGenerationMetadata,
    EdgeCaseAnalysis,
)

# Configure logging
logger = logging.getLogger(__name__)


class TestGenerationUseCase(ABC):
    """Base class for test generation use cases"""

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> List[GeneratedTest]:
        """
        Execute the use case.
        
        Returns:
            List of generated test cases
            
        Raises:
            ValueError: If input parameters are invalid
        """
        pass


class GenerateFromRequirements(TestGenerationUseCase):
    """
    Generate test cases from natural language requirements.
    
    Supports Gherkin syntax and produces structured test cases
    with steps, assertions, and test data.
    """

    def __init__(self):
        """Initialize the use case"""
        self.min_confidence = 0.7

    def execute(
        self,
        requirements: str,
        test_type: TestType = TestType.API,
        priority: TestPriority = TestPriority.MEDIUM,
        include_edge_cases: bool = False
    ) -> List[GeneratedTest]:
        """
        Generate tests from requirements.
        
        Args:
            requirements: Natural language requirements or Gherkin feature
            test_type: Type of tests to generate
            priority: Default priority for generated tests
            include_edge_cases: Whether to include edge case tests
            
        Returns:
            List of generated test cases
            
        Raises:
            ValueError: If requirements is empty or invalid
        """
        # Validate input
        if not requirements or not requirements.strip():
            raise ValueError("Requirements cannot be empty")
        
        logger.info(f"Generating tests from requirements (length: {len(requirements)})")
        
        try:
            # Parse requirements into scenarios
            scenarios = self._parse_requirements(requirements)
            logger.info(f"Parsed {len(scenarios)} scenarios")
            
            # Generate tests from each scenario
            tests: List[GeneratedTest] = []
            for scenario in scenarios:
                test = self._generate_test_from_scenario(
                    scenario, test_type, priority
                )
                tests.append(test)
            
            # Add edge cases if requested
            if include_edge_cases:
                edge_case_tests = self._generate_edge_case_tests(requirements)
                tests.extend(edge_case_tests)
                logger.info(f"Added {len(edge_case_tests)} edge case tests")
            
            logger.info(f"Generated {len(tests)} tests total")
            return tests
            
        except Exception as e:
            logger.error(f"Failed to generate tests: {e}")
            raise

    def _parse_requirements(self, requirements: str) -> List[TestScenario]:
        """Parse requirements into test scenarios"""
        scenarios = []
        
        # Simple parsing: split by "Scenario:" or "Test:"
        scenario_blocks = requirements.split("Scenario:")
        
        for block in scenario_blocks[1:]:  # Skip first empty block
            lines = block.strip().split("\n")
            name = lines[0].strip()
            description = "\n".join(lines[1:]).strip()
            
            scenario = TestScenario(
                id=str(uuid4()),
                name=name,
                description=description,
                requirements=requirements,
                generation_type=GenerationType.REQUIREMENTS,
            )
            scenarios.append(scenario)
        
        # If no scenarios found, create one from entire requirements
        if not scenarios:
            scenarios.append(TestScenario(
                id=str(uuid4()),
                name="Generated from requirements",
                description=requirements,
                requirements=requirements,
                generation_type=GenerationType.REQUIREMENTS,
            ))
        
        return scenarios

    def _generate_test_from_scenario(
        self,
        scenario: TestScenario,
        test_type: TestType,
        priority: TestPriority
    ) -> GeneratedTest:
        """Generate a test from a scenario"""
        # Parse steps from description
        steps = self._parse_steps(scenario.description)
        
        # Generate assertions
        assertions = self._generate_assertions(scenario)
        
        # Calculate confidence
        confidence = self._calculate_confidence(steps, assertions)
        
        # Create metadata
        metadata = TestGenerationMetadata(
            generation_type=GenerationType.REQUIREMENTS,
            confidence_score=confidence,
            confidence_level=self._get_confidence_level(confidence),
            model_version="local-v1.0",
            rationale="Generated from requirements analysis",
        )
        
        return GeneratedTest(
            id=str(uuid4()),
            name=scenario.name,
            description=scenario.description,
            test_code=self._generate_test_code(steps, assertions),
            test_type=test_type,
            priority=priority,
            steps=steps,
            assertions=assertions,
            metadata=metadata,
            source_requirement=scenario.requirements,
        )

    def _parse_steps(self, description: str) -> List[TestStep]:
        """Parse test steps from description"""
        steps = []
        
        # Look for Given/When/Then keywords
        keywords = ["Given", "When", "Then", "And", "But"]
        lines = description.split("\n")
        step_num = 1
        
        for line in lines:
            line = line.strip()
            if any(line.startswith(kw) for kw in keywords):
                # Extract action and expected result
                action = line
                expected = None
                
                if " should " in line.lower():
                    parts = line.split(" should ", 1)
                    action = parts[0]
                    expected = parts[1] if len(parts) > 1 else None
                
                steps.append(TestStep(
                    step_number=step_num,
                    action=action,
                    expected_result=expected or "Action completed successfully",
                ))
                step_num += 1
        
        return steps

    def _generate_assertions(self, scenario: TestScenario) -> List[TestAssertion]:
        """Generate assertions from expected outcomes"""
        assertions = []
        
        for outcome in scenario.expected_outcomes:
            assertions.append(TestAssertion(
                assertion_type="assert_equal",
                expected=outcome,
                actual="result",
                error_message=f"Expected {outcome} but got different result",
            ))
        
        return assertions

    def _calculate_confidence(
        self,
        steps: List[TestStep],
        assertions: List[TestAssertion]
    ) -> float:
        """Calculate confidence score"""
        if not steps:
            return 0.3
        
        # Base confidence
        confidence = 0.5
        
        # More steps = higher confidence (up to 0.8)
        confidence += min(len(steps) * 0.05, 0.3)
        
        # Assertions add confidence
        confidence += min(len(assertions) * 0.05, 0.2)
        
        return min(confidence, 1.0)

    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Map score to confidence level"""
        if score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.7:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _generate_test_code(
        self,
        steps: List[TestStep],
        assertions: List[TestAssertion]
    ) -> str:
        """Generate pytest code from steps and assertions"""
        code_lines = [
            '"""',
            "Generated Test Case",
            "Auto-generated from requirements",
            '"""',
            "",
            "import pytest",
            "",
            "",
            "def test_generated():",
            '    """Test generated from requirements"""',
        ]
        
        for step in steps:
            code_lines.append(f"    # Step {step.step_number}: {step.action}")
            if step.expected_result:
                code_lines.append(f"    # Expected: {step.expected_result}")
            code_lines.append("    # TODO: Implement step")
            code_lines.append("    pass")
            code_lines.append("")
        
        for assertion in assertions:
            code_lines.append(f"    {assertion.assertion_type}({assertion.actual}, {assertion.expected})")
        
        return "\n".join(code_lines)

    def _generate_edge_case_tests(self, requirements: str) -> List[GeneratedTest]:
        """Generate edge case tests from requirements"""
        # Use GenerateEdgeCases use case
        edge_gen = GenerateEdgeCases()
        return edge_gen.execute(requirements)


class GenerateFromUI(TestGenerationUseCase):
    """
    Generate E2E tests from UI analysis.
    
    Analyzes DOM structure and generates Playwright/Cypress tests
    with smart selectors.
    """

    def __init__(self):
        """Initialize the use case"""
        self.prefer_data_testid = True

    def execute(
        self,
        ui_html: str,
        framework: str = "playwright",
        include_visual_tests: bool = False
    ) -> List[GeneratedTest]:
        """
        Generate tests from UI HTML.
        
        Args:
            ui_html: HTML content of the UI to test
            framework: Test framework ('playwright' or 'cypress')
            include_visual_tests: Whether to include visual regression tests
            
        Returns:
            List of generated E2E tests
            
        Raises:
            ValueError: If ui_html is empty or framework is invalid
        """
        # Validate input
        if not ui_html or not ui_html.strip():
            raise ValueError("UI HTML cannot be empty")
        
        if framework not in ["playwright", "cypress", "generic"]:
            raise ValueError(f"Unsupported framework: {framework}")
        
        logger.info(f"Generating UI tests for {framework}")
        
        try:
            # Parse UI elements
            elements = self._parse_ui_elements(ui_html)
            logger.info(f"Parsed {len(elements)} UI elements")
            
            # Generate interactions
            interactions = self._generate_interactions(elements)
            
            # Create test cases
            tests: List[GeneratedTest] = []
            for interaction in interactions:
                test = self._create_test_from_interaction(
                    interaction, framework, elements
                )
                tests.append(test)
            
            # Add visual tests if requested
            if include_visual_tests:
                visual_tests = self._generate_visual_tests(elements)
                tests.extend(visual_tests)
                logger.info(f"Added {len(visual_tests)} visual tests")
            
            logger.info(f"Generated {len(tests)} UI tests total")
            return tests
            
        except Exception as e:
            logger.error(f"Failed to generate UI tests: {e}")
            raise

    def _parse_ui_elements(self, html: str) -> List[dict]:
        """Parse UI elements from HTML"""
        # Simple parsing: look for common elements
        elements = []
        
        # Extract buttons
        if "<button" in html:
            elements.append({
                "type": "button",
                "selector": "button",
                "action": "click",
            })
        
        # Extract inputs
        if "<input" in html:
            elements.append({
                "type": "input",
                "selector": "input",
                "action": "fill",
            })
        
        # Extract links
        if "<a " in html:
            elements.append({
                "type": "link",
                "selector": "a",
                "action": "click",
            })
        
        # Extract forms
        if "<form" in html:
            elements.append({
                "type": "form",
                "selector": "form",
                "action": "submit",
            })
        
        return elements

    def _generate_interactions(self, elements: List[dict]) -> List[dict]:
        """Generate test interactions from elements"""
        interactions = []
        
        for i, element in enumerate(elements, 1):
            interactions.append({
                "step": i,
                "element": element,
                "action": element.get("action", "interact"),
                "expected": f"{element['type']} should respond to {element.get('action', 'interaction')}",
            })
        
        return interactions

    def _create_test_from_interaction(
        self,
        interaction: dict,
        framework: str,
        elements: List[dict]
    ) -> GeneratedTest:
        """Create a test from an interaction"""
        element = interaction["element"]
        
        # Generate selector
        selector = self._generate_smart_selector(element)
        
        # Create test step
        step = TestStep(
            step_number=interaction["step"],
            action=f"{interaction['action'].capitalize()} {element['type']}",
            expected_result=interaction["expected"],
            selectors={"type": element["type"], "value": selector},
        )
        
        # Generate test code
        test_code = self._generate_framework_code(
            framework, [step], elements
        )
        
        # Create metadata
        metadata = TestGenerationMetadata(
            generation_type=GenerationType.UI_ANALYSIS,
            confidence_score=0.75,
            confidence_level=ConfidenceLevel.HIGH,
            model_version="ui-parser-v1.0",
            rationale="Generated from UI structure analysis",
        )
        
        return GeneratedTest(
            id=str(uuid4()),
            name=f"UI Test: {element['type'].capitalize()}",
            description=f"Test {element['type']} element interaction",
            test_code=test_code,
            test_type=TestType.E2E,
            priority=TestPriority.MEDIUM,
            steps=[step],
            metadata=metadata,
            framework=framework,
            source_ui_html=str(elements),
        )

    def _generate_smart_selector(self, element: dict) -> str:
        """Generate smart selector for element"""
        if self.prefer_data_testid:
            # Try to use data-testid
            return f"[data-testid='{element['type']}']"
        else:
            # Fallback to element type
            return element["selector"]

    def _generate_framework_code(
        self,
        framework: str,
        steps: List[TestStep],
        elements: List[dict]
    ) -> str:
        """Generate framework-specific test code"""
        if framework == "playwright":
            return self._generate_playwright_code(steps, elements)
        elif framework == "cypress":
            return self._generate_cypress_code(steps, elements)
        else:
            return self._generate_generic_code(steps, elements)

    def _generate_playwright_code(
        self,
        steps: List[TestStep],
        elements: List[dict]
    ) -> str:
        """Generate Playwright test code"""
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            "test('Generated UI Test', async ({ page }) => {",
        ]
        
        for step in steps:
            selector = step.selectors.get("value", "element")
            action = step.action.lower()
            
            if "click" in action:
                lines.append(f"  await page.click('{selector}');")
            elif "fill" in action or "input" in action:
                lines.append(f"  await page.fill('{selector}', 'test_value');")
            elif "submit" in action:
                lines.append(f"  await page.locator('{selector}').submit();")
            else:
                lines.append(f"  await page.locator('{selector}').{action}();")
            
            lines.append(f"  // Expected: {step.expected_result}")
        
        lines.append("});")
        
        return "\n".join(lines)

    def _generate_cypress_code(
        self,
        steps: List[TestStep],
        elements: List[dict]
    ) -> str:
        """Generate Cypress test code"""
        lines = [
            "describe('Generated UI Test', () => {",
            "  it('should interact with UI elements', () => {",
        ]
        
        for step in steps:
            selector = step.selectors.get("value", "element")
            action = step.action.lower()
            
            if "click" in action:
                lines.append(f"    cy.get('{selector}').click();")
            elif "fill" in action or "input" in action:
                lines.append(f"    cy.get('{selector}').type('test_value');")
            elif "submit" in action:
                lines.append(f"    cy.get('{selector}').submit();")
            else:
                lines.append(f"    cy.get('{selector}').{action}();")
        
        lines.append("  });")
        lines.append("});")
        
        return "\n".join(lines)

    def _generate_generic_code(
        self,
        steps: List[TestStep],
        elements: List[dict]
    ) -> str:
        """Generate generic test code"""
        lines = ["# Generated UI Test", ""]
        
        for step in steps:
            lines.append(f"Step {step.step_number}: {step.action}")
            lines.append(f"  Selector: {step.selectors}")
            lines.append(f"  Expected: {step.expected_result}")
        
        return "\n".join(lines)

    def _generate_visual_tests(self, elements: List[dict]) -> List[GeneratedTest]:
        """Generate visual regression tests"""
        tests = []
        
        for element in elements:
            test = GeneratedTest(
                id=str(uuid4()),
                name=f"Visual Test: {element['type'].capitalize()}",
                description=f"Visual regression test for {element['type']}",
                test_code=f"await expect(page.locator('{element['selector']}')).toHaveScreenshot();",
                test_type=TestType.E2E,
                priority=TestPriority.LOW,
                metadata=TestGenerationMetadata(
                    generation_type=GenerationType.UI_ANALYSIS,
                    confidence_score=0.8,
                    confidence_level=ConfidenceLevel.HIGH,
                    model_version="visual-v1.0",
                    rationale="Visual regression test",
                ),
            )
            tests.append(test)
        
        return tests


class GenerateEdgeCases(TestGenerationUseCase):
    """
    Generate edge case tests using boundary value analysis,
    equivalence partitioning, and error path testing.
    """

    def __init__(self):
        """Initialize the use case"""
        self.boundary_strategies = [
            EdgeCaseType.BOUNDARY_VALUE,
            EdgeCaseType.EQUIVALENCE_PARTITIONING,
            EdgeCaseType.ERROR_PATH,
            EdgeCaseType.NEGATIVE,
        ]

    def execute(
        self,
        requirements: str,
        input_types: Optional[List[str]] = None,
        max_cases: int = 10
    ) -> List[GeneratedTest]:
        """
        Generate edge case tests.
        
        Args:
            requirements: Requirements or description to analyze
            input_types: Types of inputs to consider (e.g., 'string', 'number')
            max_cases: Maximum number of edge cases to generate
            
        Returns:
            List of edge case test cases
            
        Raises:
            ValueError: If requirements is empty or max_cases is invalid
        """
        # Validate input
        if not requirements or not requirements.strip():
            raise ValueError("Requirements cannot be empty")
        
        if max_cases < 1:
            raise ValueError("max_cases must be at least 1")
        
        logger.info(f"Generating edge cases (max: {max_cases})")
        
        try:
            # Identify input parameters
            parameters = self._identify_parameters(requirements, input_types)
            logger.info(f"Identified {len(parameters)} parameters")
            
            # Generate edge cases for each parameter
            edge_cases: List[EdgeCase] = []
            
            for param in parameters[:max_cases]:
                # Boundary value analysis
                boundary_cases = self._generate_boundary_cases(param)
                edge_cases.extend(boundary_cases)
                
                # Equivalence partitioning
                partition_cases = self._generate_partition_cases(param)
                edge_cases.extend(partition_cases)
                
                # Error paths
                error_cases = self._generate_error_path_cases(param)
                edge_cases.extend(error_cases)
            
            # Convert to GeneratedTest objects
            tests: List[GeneratedTest] = []
            for edge_case in edge_cases[:max_cases]:
                test = self._edge_case_to_test(edge_case)
                tests.append(test)
            
            logger.info(f"Generated {len(tests)} edge case tests")
            return tests
            
        except Exception as e:
            logger.error(f"Failed to generate edge cases: {e}")
            raise

    def _identify_parameters(
        self,
        requirements: str,
        input_types: Optional[List[str]]
    ) -> List[dict]:
        """Identify input parameters from requirements"""
        # Simple parameter extraction
        parameters = []
        
        # Look for common patterns
        if "username" in requirements.lower():
            parameters.append({
                "name": "username",
                "type": "string",
                "min": 3,
                "max": 50,
            })
        
        if "email" in requirements.lower():
            parameters.append({
                "name": "email",
                "type": "email",
                "pattern": "email",
            })
        
        if "password" in requirements.lower():
            parameters.append({
                "name": "password",
                "type": "string",
                "min": 8,
                "max": 100,
            })
        
        if "age" in requirements.lower() or "number" in requirements.lower():
            parameters.append({
                "name": "age",
                "type": "number",
                "min": 0,
                "max": 150,
            })
        
        # Default parameters if none found
        if not parameters:
            parameters.append({
                "name": "input",
                "type": "string",
                "min": 1,
                "max": 255,
            })
        
        return parameters

    def _generate_boundary_cases(self, param: dict) -> List[EdgeCase]:
        """Generate boundary value test cases"""
        cases = []
        
        min_val = param.get("min", 0)
        max_val = param.get("max", 100)
        
        # Min boundary
        cases.append(EdgeCase(
            id=str(uuid4()),
            name=f"Boundary: {param['name']} at minimum ({min_val})",
            description=f"Test {param['name']} at minimum allowed value",
            edge_case_type=EdgeCaseType.BOUNDARY_VALUE,
            input_conditions={param["name"]: min_val},
            expected_behavior="System should accept minimum value",
            severity=TestPriority.HIGH,
            likelihood=0.8,
        ))
        
        # Max boundary
        cases.append(EdgeCase(
            id=str(uuid4()),
            name=f"Boundary: {param['name']} at maximum ({max_val})",
            description=f"Test {param['name']} at maximum allowed value",
            edge_case_type=EdgeCaseType.BOUNDARY_VALUE,
            input_conditions={param["name"]: max_val},
            expected_behavior="System should accept maximum value",
            severity=TestPriority.HIGH,
            likelihood=0.8,
        ))
        
        # Below min
        cases.append(EdgeCase(
            id=str(uuid4()),
            name=f"Boundary: {param['name']} below minimum",
            description=f"Test {param['name']} below minimum allowed value",
            edge_case_type=EdgeCaseType.BOUNDARY_VALUE,
            input_conditions={param["name"]: min_val - 1},
            expected_behavior="System should reject value below minimum",
            severity=TestPriority.MEDIUM,
            likelihood=0.7,
        ))
        
        # Above max
        cases.append(EdgeCase(
            id=str(uuid4()),
            name=f"Boundary: {param['name']} above maximum",
            description=f"Test {param['name']} above maximum allowed value",
            edge_case_type=EdgeCaseType.BOUNDARY_VALUE,
            input_conditions={param["name"]: max_val + 1},
            expected_behavior="System should reject value above maximum",
            severity=TestPriority.MEDIUM,
            likelihood=0.7,
        ))
        
        return cases

    def _generate_partition_cases(self, param: dict) -> List[EdgeCase]:
        """Generate equivalence partitioning test cases"""
        cases = []
        
        param_type = param.get("type", "string")
        
        # Valid partition
        cases.append(EdgeCase(
            id=str(uuid4()),
            name=f"Partition: Valid {param['name']}",
            description=f"Test {param['name']} with valid value",
            edge_case_type=EdgeCaseType.EQUIVALENCE_PARTITIONING,
            input_conditions={param["name"]: self._get_valid_value(param_type)},
            expected_behavior="System should accept valid value",
            severity=TestPriority.MEDIUM,
            likelihood=0.9,
        ))
        
        # Invalid partition (type mismatch)
        cases.append(EdgeCase(
            id=str(uuid4()),
            name=f"Partition: Invalid type for {param['name']}",
            description=f"Test {param['name']} with wrong type",
            edge_case_type=EdgeCaseType.EQUIVALENCE_PARTITIONING,
            input_conditions={param["name"]: self._get_invalid_type_value(param_type)},
            expected_behavior="System should reject invalid type",
            severity=TestPriority.HIGH,
            likelihood=0.6,
        ))
        
        # Empty/null partition
        cases.append(EdgeCase(
            id=str(uuid4()),
            name=f"Partition: Empty {param['name']}",
            description=f"Test {param['name']} with empty value",
            edge_case_type=EdgeCaseType.EQUIVALENCE_PARTITIONING,
            input_conditions={param["name"]: ""},
            expected_behavior="System should handle empty input",
            severity=TestPriority.HIGH,
            likelihood=0.8,
        ))
        
        return cases

    def _generate_error_path_cases(self, param: dict) -> List[EdgeCase]:
        """Generate error path test cases"""
        cases = []
        
        param_type = param.get("type", "string")
        
        # SQL injection attempt
        if param_type in ["string", "email"]:
            cases.append(EdgeCase(
                id=str(uuid4()),
                name=f"Error Path: SQL injection in {param['name']}",
                description=f"Test {param['name']} with SQL injection attempt",
                edge_case_type=EdgeCaseType.ERROR_PATH,
                input_conditions={param["name"]: "'; DROP TABLE users; --"},
                expected_behavior="System should sanitize or reject malicious input",
                severity=TestPriority.CRITICAL,
                likelihood=0.3,
            ))
        
        # XSS attempt
        if param_type in ["string", "email"]:
            cases.append(EdgeCase(
                id=str(uuid4()),
                name=f"Error Path: XSS in {param['name']}",
                description=f"Test {param['name']} with XSS attempt",
                edge_case_type=EdgeCaseType.ERROR_PATH,
                input_conditions={param["name"]: "<script>alert('XSS')</script>"},
                expected_behavior="System should sanitize or reject malicious input",
                severity=TestPriority.CRITICAL,
                likelihood=0.3,
            ))
        
        # Very long input
        cases.append(EdgeCase(
            id=str(uuid4()),
            name=f"Error Path: Very long {param['name']}",
            description=f"Test {param['name']} with extremely long value",
            edge_case_type=EdgeCaseType.ERROR_PATH,
            input_conditions={param["name"]: "A" * 10000},
            expected_behavior="System should handle or truncate long input",
            severity=TestPriority.MEDIUM,
            likelihood=0.5,
        ))
        
        return cases

    def _get_valid_value(self, param_type: str) -> str:
        """Get a valid value for parameter type"""
        values = {
            "string": "test_value",
            "email": "test@example.com",
            "number": "42",
            "boolean": "true",
        }
        return values.get(param_type, "test")

    def _get_invalid_type_value(self, param_type: str) -> str:
        """Get an invalid type value for parameter type"""
        if param_type == "number":
            return "not_a_number"
        elif param_type == "email":
            return "not_an_email"
        elif param_type == "boolean":
            return "not_a_boolean"
        else:
            return "12345"  # Number for string type

    def _edge_case_to_test(self, edge_case: EdgeCase) -> GeneratedTest:
        """Convert EdgeCase to GeneratedTest"""
        return GeneratedTest(
            id=str(uuid4()),
            name=edge_case.name,
            description=edge_case.description,
            test_code=edge_case._generate_edge_case_code(),
            test_type=TestType.REGRESSION,
            priority=edge_case.severity,
            tags=["edge_case", edge_case.edge_case_type.value],
            preconditions=edge_case._generate_preconditions(),
            metadata=TestGenerationMetadata(
                generation_type=GenerationType.EDGE_CASE,
                confidence_score=0.7,
                confidence_level=ConfidenceLevel.HIGH,
                model_version="edge-gen-v1.0",
                rationale=f"Generated from {edge_case.edge_case_type.value} analysis",
            ),
        )
