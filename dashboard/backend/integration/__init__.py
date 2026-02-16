"""
Integration Module

Provides integration with external systems including the existing QA-FRAMEWORK.
"""
from qa_framework_client import (
    QAFrameworkClient,
    execute_qa_test_suite,
    get_qa_test_suites
)

__all__ = [
    'QAFrameworkClient',
    'execute_qa_test_suite',
    'get_qa_test_suites'
]