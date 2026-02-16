"""
Integration Hub Example Usage

Examples showing how to use the Integration Hub for various scenarios.
"""
import asyncio
from datetime import datetime
from typing import Dict, List

from backend.integrations.manager import integration_manager
from backend.integrations.base import TestResult, TestStatus


async def example_configure_and_sync():
    """
    Example: Configure Jira and sync test results
    
    This demonstrates the typical workflow for setting up an integration
    and using it to sync test results.
    """
    print("=== Example 1: Configure Jira and sync test results ===\n")
    
    # Define Jira configuration
    jira_config = {
        "base_url": "https://yourcompany.atlassian.net",
        "email": "qa@yourcompany.com",
        "api_token": "your_jira_api_token",
        "default_project": "QA",
        "auto_create_bugs": True
    }
    
    try:
        # Register Jira integration
        print("1. Registering Jira integration...")
        integration_manager.register_integration("jira", jira_config)
        print("   ✅ Jira integration registered\n")
        
        # Connect to Jira
        print("2. Connecting to Jira...")
        connected = await integration_manager.connect_integration("jira")
        if connected:
            print("   ✅ Connected to Jira successfully\n")
        else:
            print("   ❌ Failed to connect to Jira\n")
            return
        
        # Create sample test results
        print("3. Creating sample test results...")
        sample_results = [
            TestResult(
                test_id="test_login_001",
                test_name="User Login Authentication",
                classname="auth.tests.LoginTest",
                status=TestStatus.PASSED,
                duration=2.45,
                message="Login with valid credentials succeeded",
                tags=["auth", "smoke", "critical"],
                metadata={"browser": "chrome", "environment": "staging"}
            ),
            TestResult(
                test_id="test_logout_002",
                test_name="User Logout Functionality",
                classname="auth.tests.LogoutTest",
                status=TestStatus.FAILED,
                duration=1.78,
                message="Logout failed due to session timeout",
                error="AssertionError: Expected redirect after logout",
                stack_trace="Traceback: ...",
                tags=["auth", "smoke", "critical"],
                metadata={"browser": "firefox", "environment": "staging"}
            ),
            TestResult(
                test_id="test_password_reset_003",
                test_name="Password Reset Flow",
                classname="auth.tests.PasswordResetTest",
                status=TestStatus.PASSED,
                duration=5.12,
                message="Password reset flow completed successfully",
                tags=["auth", "regression"],
                metadata={"browser": "safari", "environment": "staging"}
            )
        ]
        print(f"   ✅ Created {len(sample_results)} sample test results\n")
        
        # Sync results to Jira
        print("4. Syncing test results to Jira...")
        sync_results = await integration_manager.sync_test_results(
            results=sample_results,
            providers=["jira"],
            project_key="QA"
        )
        
        for provider, result in sync_results.items():
            print(f"   Provider: {provider}")
            print(f"   Success: {result.success}")
            print(f"   Synced: {result.synced_count}")
            print(f"   Failed: {result.failed_count}")
            if result.errors:
                print(f"   Errors: {result.errors}")
            print(f"   Details: {result.details}")
        print()
        
    except Exception as e:
        print(f"❌ Error in example: {str(e)}")


async def example_multi_provider_sync():
    """
    Example: Sync to multiple providers simultaneously
    
    Demonstrates how to sync the same test results to multiple providers.
    """
    print("=== Example 2: Multi-provider sync (Jira + Zephyr) ===\n")
    
    # Configure Jira
    jira_config = {
        "base_url": "https://yourcompany.atlassian.net",
        "email": "qa@yourcompany.com",
        "api_token": "your_jira_api_token",
        "default_project": "QA",
        "auto_create_bugs": True
    }
    
    # Configure Zephyr (uses same Jira credentials)
    zephyr_config = {
        "jira_base_url": "https://yourcompany.atlassian.net",
        "jira_email": "qa@yourcompany.com",
        "jira_api_token": "your_jira_api_token",
        "default_project": "QA",
        "auto_create_cycles": True
    }
    
    try:
        # Register both integrations
        print("1. Registering Jira and Zephyr integrations...")
        integration_manager.register_integration("jira", jira_config)
        integration_manager.register_integration("zephyr", zephyr_config)
        print("   ✅ Both integrations registered\n")
        
        # Connect to both
        print("2. Connecting to both providers...")
        jira_connected = await integration_manager.connect_integration("jira")
        zephyr_connected = await integration_manager.connect_integration("zephyr")
        
        if jira_connected and zephyr_connected:
            print("   ✅ Both providers connected successfully\n")
        else:
            print(f"   ❌ Connection failed - Jira: {jira_connected}, Zephyr: {zephyr_connected}")
            return
        
        # Sample test results
        sample_results = [
            TestResult(
                test_id="api_test_001",
                test_name="API Health Check",
                classname="api.tests.HealthTest",
                status=TestStatus.PASSED,
                duration=0.23,
                tags=["api", "health", "critical"]
            ),
            TestResult(
                test_id="api_test_002",
                test_name="API Authentication",
                classname="api.tests.AuthTest",
                status=TestStatus.FAILED,
                duration=1.45,
                error="Unauthorized: Missing auth header",
                tags=["api", "auth", "critical"]
            )
        ]
        
        # Sync to both providers
        print("3. Syncing to both Jira and Zephyr...")
        sync_results = await integration_manager.sync_test_results(
            results=sample_results,
            providers=["jira", "zephyr"],  # Sync to both
            project_key="QA",
            cycle_name=f"API Tests {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        for provider, result in sync_results.items():
            print(f"   {provider.upper()}:")
            print(f"     Success: {result.success}")
            print(f"     Synced: {result.synced_count}")
            print(f"     Failed: {result.failed_count}")
        print()
        
    except Exception as e:
        print(f"❌ Error in multi-provider example: {str(e)}")


async def example_health_checks():
    """
    Example: Perform health checks on configured integrations
    """
    print("=== Example 3: Health checks ===\n")
    
    try:
        # Register a dummy integration to demonstrate health checks
        dummy_config = {
            "base_url": "https://test.atlassian.net",
            "email": "test@example.com",
            "api_token": "dummy_token",
            "default_project": "TEST"
        }
        
        print("1. Registering test integration...")
        integration_manager.register_integration("jira", dummy_config)
        print("   ✅ Test integration registered\n")
        
        # Perform health check
        print("2. Performing health check...")
        health = await integration_manager.health_check("jira")
        print(f"   Health status: {health}")
        print()
        
        # Check all configured integrations
        print("3. Checking health of all configured integrations...")
        all_health = await integration_manager.get_all_health_status()
        for provider, status in all_health.items():
            print(f"   {provider}: {status.get('status', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Error in health check example: {str(e)}")


async def example_bulk_operations():
    """
    Example: Bulk operations with different configurations per provider
    """
    print("=== Example 4: Bulk operations with different configs ===\n")
    
    # Configure multiple providers with different settings
    configs = {
        "jira": {
            "base_url": "https://company1.atlassian.net",
            "email": "qa@company1.com",
            "api_token": "token1",
            "default_project": "PROJ1"
        },
        "zephyr": {
            "jira_base_url": "https://company1.atlassian.net",
            "jira_email": "qa@company1.com",
            "jira_api_token": "token1",
            "default_project": "PROJ1"
        }
    }
    
    try:
        # Register integrations
        for provider, config in configs.items():
            integration_manager.register_integration(provider, config)
        
        print("1. Registered multiple integrations with different configs\n")
        
        # Sample results
        sample_results = [
            TestResult(
                test_id="perf_test_001",
                test_name="Performance Load Test",
                status=TestStatus.PASSED,
                duration=120.5,
                tags=["performance", "load"]
            )
        ]
        
        # Bulk sync with different mappings
        mappings = {
            "jira": {"project_key": "PROJ1", "cycle_name": "Load Test Cycle"},
            "zephyr": {"project_key": "PROJ1", "cycle_name": "Performance Run"}
        }
        
        print("2. Performing bulk sync with different configurations...")
        bulk_results = await integration_manager.bulk_sync(
            results=sample_results,
            mappings=mappings
        )
        
        for provider, result in bulk_results.items():
            print(f"   {provider}: {result}")
        print()
        
    except Exception as e:
        print(f"❌ Error in bulk operations example: {str(e)}")


async def example_crud_operations():
    """
    Example: CRUD operations on test cases and bugs
    """
    print("=== Example 5: CRUD operations (Test cases & Bugs) ===\n")
    
    jira_config = {
        "base_url": "https://yourcompany.atlassian.net",
        "email": "qa@yourcompany.com",
        "api_token": "your_jira_api_token",
        "default_project": "QA"
    }
    
    try:
        # Register and connect
        integration_manager.register_integration("jira", jira_config)
        await integration_manager.connect_integration("jira")
        
        print("1. Creating a test case...")
        test_case = await integration_manager.create_test_case(
            provider="jira",
            name="API Authentication Test",
            description="Test that API endpoints require proper authentication",
            project_key="QA",
            labels=["api", "auth", "automated"]
        )
        print(f"   Created test case: {test_case}\n")
        
        print("2. Getting test cases...")
        test_cases = await integration_manager.get_test_cases(
            provider="jira",
            project_key="QA",
            filters={"labels": ["api", "auth"]}
        )
        print(f"   Found {len(test_cases)} test cases\n")
        
        print("3. Creating a bug from a failed test...")
        # Simulate a failed test result
        failed_result = TestResult(
            test_id="api_test_005",
            test_name="API Rate Limiting",
            status=TestStatus.FAILED,
            duration=3.2,
            error="API not respecting rate limits"
        )
        
        bug = await integration_manager.create_bug(
            provider="jira",
            title="[QA] API Not Respecting Rate Limits",
            description="The API is not properly implementing rate limiting as expected.",
            project_key="QA",
            test_result=failed_result,
            severity="High",
            priority="High",
            labels=["bug", "api", "regression"]
        )
        print(f"   Created bug: {bug}\n")
        
        print("4. Getting bugs...")
        bugs = await integration_manager.get_bugs(
            provider="jira",
            project_key="QA",
            status="Open"
        )
        print(f"   Found {len(bugs)} open bugs\n")
        
    except Exception as e:
        print(f"❌ Error in CRUD operations example: {str(e)}")


async def run_all_examples():
    """
    Run all examples to demonstrate the Integration Hub capabilities
    """
    print("🧪 QA-FRAMEWORK Integration Hub Examples\n")
    print("This demonstrates the various capabilities of the Integration Hub.\n")
    
    await example_configure_and_sync()
    await example_multi_provider_sync()
    await example_health_checks()
    await example_bulk_operations()
    await example_crud_operations()
    
    print("🎉 All examples completed!")
    print("\n💡 Key benefits of the Integration Hub:")
    print("   • Pluggable architecture - easy to add new providers")
    print("   • Consistent interface across all providers")
    print("   • Bulk operations across multiple providers")
    print("   • Health monitoring and error handling")
    print("   • Comprehensive configuration validation")
    print("   • Support for all major test management tools")


if __name__ == "__main__":
    asyncio.run(run_all_examples())
