"""
Entities for Test Generation Domain

Defines core domain entities for AI-powered test generation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
import logging

from pydantic import BaseModel, Field, validator

from .value_objects import (
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


class GeneratedTest(BaseModel):
    """
    Represents a complete generated test case.

    This is the main entity that holds all information about
    an AI-generated test including code, metadata, and execution details.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    test_code: str = Field(..., min_length=10)
    test_type: TestType = TestType.API
    priority: TestPriority = TestPriority.MEDIUM

    steps: List[TestStep] = Field(default_factory=list)
    assertions: List[TestAssertion] = Field(default_factory=list)
    test_data: Optional[TestData] = None

    gherkin_scenario: Optional[GherkinScenario] = None

    metadata: Optional[TestGenerationMetadata] = None

    tags: List[str] = Field(default_factory=list)
    preconditions: List[str] = Field(default_factory=list)
    postconditions: List[str] = Field(default_factory=list)

    framework: str = "pytest"
    language: str = "python"

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    source_requirement: Optional[str] = None
    source_ui_html: Optional[str] = None
    parent_test_id: Optional[str] = None

    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate test name is meaningful"""
        if not v or not v.strip():
            raise ValueError("Test name cannot be empty")
        return v.strip()
    
    @validator('test_code')
    def validate_test_code(cls, v: str) -> str:
        """Validate test code has minimum content"""
        if len(v.strip()) < 10:
            raise ValueError("Test code must have at least 10 characters")
        return v

    def add_step(self, step: TestStep) -> None:
        """
        Add a test step to the test.
        
        Args:
            step: TestStep to add
        """
        if not step:
            logger.warning("Attempted to add empty step")
            return
        self.steps.append(step)
        self.updated_at = datetime.now()
        logger.debug(f"Added step {step.step_number}: {step.action}")

    def add_assertion(self, assertion: TestAssertion) -> None:
        """
        Add an assertion to the test.
        
        Args:
            assertion: TestAssertion to add
        """
        if not assertion:
            logger.warning("Attempted to add empty assertion")
            return
        self.assertions.append(assertion)
        self.updated_at = datetime.now()
        logger.debug(f"Added assertion: {assertion.assertion_type}")

    def get_confidence_level(self) -> ConfidenceLevel:
        """
        Get the confidence level based on score.
        
        Returns:
            ConfidenceLevel enum value
        """
        if self.metadata is None:
            logger.debug("No metadata available, returning MEDIUM confidence")
            return ConfidenceLevel.MEDIUM
        return self.metadata.confidence_level

    def to_playwright_format(self) -> str:
        """Convert to Playwright E2E test format"""
        code_lines = [
            f"// Test: {self.name}",
            f"// Generated: {self.created_at.isoformat()}",
            f"import {{ test, expect }} from '@playwright/test';",
            "",
            f"test('{self.name}', async ({{ page }}) => {{",
        ]

        for step in self.steps:
            if step.selectors:
                selector_type = list(step.selectors.keys())[0]
                selector_value = list(step.selectors.values())[0]
                code_lines.append(f"  // {step.step_number}. {step.action}")
                code_lines.append(
                    f"  await page.{self._get_playwright_action(selector_type, selector_value)}('{selector_value}');"
                )
            else:
                code_lines.append(f"  // {step.step_number}. {step.action}")

            if step.expected_result:
                code_lines.append(f"  // Expected: {step.expected_result}")

        for assertion in self.assertions:
            code_lines.append(
                f"  await expect({assertion.actual}).{assertion.assertion_type}({assertion.expected});"
            )

        code_lines.append("});")

        return "\n".join(code_lines)

    def to_pytest_format(self) -> str:
        """Convert to Pytest format"""
        code_lines = [
            f'"""',
            f"Test: {self.name}",
            f"Description: {self.description}",
            f'"""',
            "",
            "import pytest",
            "",
        ]

        if self.preconditions:
            code_lines.append("@pytest.fixture")
            code_lines.append("def setup_test():")
            for precond in self.preconditions:
                code_lines.append(f"    # {precond}")
            code_lines.append("    pass")
            code_lines.append("")

        code_lines.append(f"def test_{self._sanitize_name(self.name)}():")
        code_lines.append(f'    """{self.description}"""')

        for step in self.steps:
            code_lines.append(f"    # {step.step_number}. {step.action}")
            if step.test_data:
                code_lines.append(f"    # Test data: {step.test_data}")
            if step.expected_result:
                code_lines.append(f"    # Expected: {step.expected_result}")

        for assertion in self.assertions:
            code_lines.append(
                f"    {assertion.assertion_type}({assertion.actual}, {assertion.expected})"
            )

        code_lines.append("")

        if self.tags:
            code_lines.append(f"@pytest.mark.{' @pytest.mark.'.join(self.tags)}")

        return "\n".join(code_lines)

    def to_gherkin_format(self) -> str:
        """Convert to Gherkin BDD format"""
        if self.gherkin_scenario:
            scenario = self.gherkin_scenario
            lines = []

            if scenario.tags:
                lines.extend([f"@{tag}" for tag in scenario.tags])

            lines.append(f"Feature: {scenario.feature}")
            lines.append("")

            if scenario.background:
                lines.append(f"  Background:")
                lines.append(f"    {scenario.background}")
                lines.append("")

            lines.append(f"  Scenario: {scenario.scenario_name}")

            for step in self.steps:
                step_keyword = self._get_gherkin_keyword(step.step_number)
                lines.append(f"    {step_keyword} {step.action}")
                if step.expected_result:
                    lines.append(f"      Then {step.expected_result}")

            return "\n".join(lines)

        lines = [
            f"Feature: {self.name}",
            f"  {self.description}",
            "",
            f"  Scenario: {self.name}",
        ]

        for step in self.steps:
            keyword = self._get_gherkin_keyword(step.step_number)
            lines.append(f"    {keyword} {step.action}")
            if step.expected_result:
                lines.append(f"    Then {step.expected_result}")

        return "\n".join(lines)

    def _get_playwright_action(self, selector_type: str, selector_value: str) -> str:
        """Map selector type to Playwright action"""
        mapping = {
            "id": "getById",
            "class": "locator",
            "tag": "locator",
            "attribute": "getByAttribute",
            "xpath": "locator",
            "css": "locator",
            "text": "getByText",
            "role": "getByRole",
        }
        return mapping.get(selector_type, "locator")

    def _sanitize_name(self, name: str) -> str:
        """Sanitize test name for Python function"""
        return name.lower().replace(" ", "_").replace("-", "_").replace(".", "_")

    def _get_gherkin_keyword(self, step_number: int) -> str:
        """Map step number to Gherkin keyword"""
        if step_number == 1:
            return "Given"
        elif step_number % 3 == 2:
            return "When"
        else:
            return "Then"


class TestScenario(BaseModel):
    """
    Represents a test scenario that can generate multiple test cases.

    A scenario defines a testing context from which individual
    test cases can be derived.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1)
    description: str
    requirements: str

    generation_type: GenerationType
    test_types: List[TestType] = Field(default_factory=list)

    expected_outcomes: List[str] = Field(default_factory=list)
    user_personas: List[str] = Field(default_factory=list)

    ui_elements: List = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_requirement(self, requirement: str) -> None:
        """Add a requirement to the scenario"""
        self.requirements += f"\n- {requirement}"
        self.updated_at = datetime.now()

    def add_expected_outcome(self, outcome: str) -> None:
        """Add an expected outcome"""
        self.expected_outcomes.append(outcome)
        self.updated_at = datetime.now()


class EdgeCase(BaseModel):
    """
    Represents an edge case for test generation.

    Edge cases are boundary conditions, error paths, and
    unusual scenarios that tests should cover.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1)
    description: str

    edge_case_type: EdgeCaseType

    input_conditions: dict = Field(default_factory=dict)
    expected_behavior: str

    severity: TestPriority = TestPriority.MEDIUM
    likelihood: float = Field(..., ge=0.0, le=1.0)

    related_tests: List[str] = Field(default_factory=list)
    mitigation_steps: List[str] = Field(default_factory=list)

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def calculate_risk_score(self) -> float:
        """Calculate risk score based on severity and likelihood"""
        severity_weights = {
            TestPriority.LOW: 0.25,
            TestPriority.MEDIUM: 0.5,
            TestPriority.HIGH: 0.75,
            TestPriority.CRITICAL: 1.0,
        }
        return severity_weights.get(self.severity, 0.5) * self.likelihood

    def to_test_case(self) -> GeneratedTest:
        """Convert edge case to a test case"""
        return GeneratedTest(
            name=f"Edge Case: {self.name}",
            description=self.description,
            test_code=self._generate_edge_case_code(),
            test_type=TestType.REGRESSION,
            priority=self.severity,
            tags=["edge_case", self.edge_case_type.value],
            preconditions=self._generate_preconditions(),
            postconditions=["Test cleanup completed"],
        )

    def _generate_edge_case_code(self) -> str:
        """Generate pytest code for this edge case"""
        return f'''def test_edge_case_{self.id[:8]}():
    """
    Edge Case: {self.name}
    Type: {self.edge_case_type.value}
    Severity: {self.severity.value}
    """
    # Input conditions: {self.input_conditions}
    # Expected behavior: {self.expected_behavior}
    
    # TODO: Implement edge case test
    assert True, "Edge case test pending implementation"
'''

    def _generate_preconditions(self) -> List[str]:
        """Generate precondition strings"""
        preconditions = ["System is operational"]
        for key, value in self.input_conditions.items():
            preconditions.append(f"Set {key} = {value}")
        return preconditions
