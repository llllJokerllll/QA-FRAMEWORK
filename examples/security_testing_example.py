"""
Security Testing Example - QA-FRAMEWORK

This example demonstrates how to use the Security Testing Module
to test web applications for common vulnerabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.adapters.security import (
    SecurityClient,
    SQLInjectionTester,
    XSSTester,
    AuthTester,
    AuthTestCase,
)
from src.adapters.security.auth_tester import AuthTestType
from src.adapters.http import HTTPXClient


async def example_sql_injection_test():
    """
    Example 1: Test for SQL Injection vulnerabilities.

    This tests URL parameters for SQL injection vulnerabilities
    using various payloads.
    """
    print("=" * 60)
    print("EXAMPLE 1: SQL Injection Testing")
    print("=" * 60)

    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = SecurityClient(http_client)

    try:
        # Test a parameter for SQL injection
        # Note: httpbin.org is safe and won't actually have vulnerabilities
        # This is just to demonstrate the API
        results = await client.test_sql_injection(target_url="/get", parameter="id", method="GET")

        print(f"\nSQL Injection Test Results:")
        print(f"  Parameter: {results['parameter']}")
        print(f"  Vulnerable: {results['vulnerable']}")
        print(f"  Total Tests: {len(results['all_tests'])}")

        if results["vulnerable"]:
            print(f"\n  Vulnerabilities Found: {results['vulnerabilities_count']}")
            for vuln in results["vulnerabilities"]:
                print(f"    - Type: {vuln['injection_type']}")
                print(f"      Payload: {vuln['payload']}")
        else:
            print("\n  No SQL injection vulnerabilities detected.")

        print(f"\n  Recommendations:")
        for rec in results["recommendations"][:3]:
            print(f"    • {rec}")

    except Exception as e:
        print(f"Error running SQL injection test: {e}")
    finally:
        await client.close()


async def example_xss_test():
    """
    Example 2: Test for Cross-Site Scripting (XSS) vulnerabilities.

    This tests URL parameters for XSS vulnerabilities.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: XSS Testing")
    print("=" * 60)

    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = SecurityClient(http_client)

    try:
        # Test a parameter for XSS
        results = await client.test_xss(target_url="/get", parameter="search", method="GET")

        print(f"\nXSS Test Results:")
        print(f"  Parameter: {results['parameter']}")
        print(f"  Vulnerable: {results['vulnerable']}")
        print(f"  Total Tests: {len(results['all_tests'])}")

        if results["vulnerable"]:
            print(f"\n  Vulnerabilities Found: {results['vulnerabilities_count']}")
            for vuln in results["vulnerabilities"]:
                print(f"    - Type: {vuln['xss_type']}")
                print(f"      Severity: {vuln['severity']}")
        else:
            print("\n  No XSS vulnerabilities detected.")

        print(f"\n  Recommendations:")
        for rec in results["recommendations"][:3]:
            print(f"    • {rec}")

    except Exception as e:
        print(f"Error running XSS test: {e}")
    finally:
        await client.close()


async def example_authentication_test():
    """
    Example 3: Test authentication mechanisms.

    This tests authentication endpoints for common vulnerabilities.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Authentication Testing")
    print("=" * 60)

    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = SecurityClient(http_client)

    try:
        # Define authentication test cases
        test_cases = [
            AuthTestCase(
                name="Test weak password",
                test_type=AuthTestType.PASSWORD_POLICY,
                username="testuser",
                password="123",
                expected_success=False,
                description="Test that weak passwords are rejected",
            ),
            AuthTestCase(
                name="Test SQL injection in username",
                test_type=AuthTestType.CREDENTIAL_STUFFING,
                username="' OR '1'='1",
                password="anything",
                expected_success=False,
                description="Test SQL injection protection",
            ),
        ]

        # Run authentication tests
        results = await client.test_authentication(target_url="/post", test_cases=test_cases)

        print(f"\nAuthentication Test Results:")
        print(f"  Total Tests: {results['total_tests']}")
        print(f"  Successful Logins: {results['successful_logins']}")
        print(f"  Vulnerabilities Found: {results['vulnerabilities_found']}")

        print(f"\n  Test Results:")
        for result in results["results"]:
            status = "✓ PASS" if not result["vulnerable"] else "✗ FAIL"
            print(f"    {status}: {result['name']}")

        if results["security_issues"]:
            print(f"\n  Security Issues:")
            for issue in results["security_issues"]:
                print(f"    • [{issue['severity'].upper()}] {issue['description']}")

    except Exception as e:
        print(f"Error running authentication test: {e}")
    finally:
        await client.close()


async def example_common_credentials_test():
    """
    Example 4: Test for common/default credentials.

    This attempts to login with common username/password combinations.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Common Credentials Testing")
    print("=" * 60)

    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = SecurityClient(http_client)

    try:
        # Test for common credentials
        results = await client.test_common_credentials(
            login_url="/post", username_field="username", password_field="password"
        )

        print(f"\nCommon Credentials Test Results:")
        print(f"  Total Tests: {results['total_tests']}")
        print(f"  Successful Logins: {results['successful_logins']}")
        print(f"  Vulnerabilities Found: {results['vulnerabilities_found']}")

        if results["vulnerabilities_found"] > 0:
            print(f"\n  WARNING: Common credentials may be accepted!")
            print(f"  This is a critical security vulnerability.")
        else:
            print("\n  Good: Common credentials were rejected.")

    except Exception as e:
        print(f"Error running common credentials test: {e}")
    finally:
        await client.close()


async def example_rate_limiting_test():
    """
    Example 5: Test rate limiting implementation.

    This tests if API endpoints properly implement rate limiting.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Rate Limiting Testing")
    print("=" * 60)

    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = SecurityClient(http_client)

    try:
        # Test rate limiting
        results = await client.test_rate_limiting(
            target_url="/get", requests_count=50, time_window=10
        )

        print(f"\nRate Limiting Test Results:")
        print(f"  Target: {results['target_url']}")
        print(f"  Requests Sent: {results['requests_sent']}")
        print(f"  Blocked: {results['blocked_requests']}")
        print(f"  Allowed: {results['allowed_requests']}")
        print(f"  Properly Configured: {results['properly_configured']}")

        analysis = results.get("analysis", {})
        print(f"\n  Analysis:")
        print(f"    Has Rate Limiting: {analysis.get('has_rate_limiting', False)}")
        print(f"    Block Rate: {analysis.get('block_rate', 0):.2%}")

        if not results["properly_configured"]:
            print(f"\n  WARNING: Rate limiting may not be properly configured!")

        print(f"\n  Recommendations:")
        for rec in results["recommendations"][:3]:
            print(f"    • {rec}")

    except Exception as e:
        print(f"Error running rate limiting test: {e}")
    finally:
        await client.close()


async def example_security_headers_test():
    """
    Example 6: Test security headers.

    This checks if the application returns proper security headers.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Security Headers Testing")
    print("=" * 60)

    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = SecurityClient(http_client)

    try:
        # Test security headers
        results = await client.test_security_headers("/get")

        print(f"\nSecurity Headers Test Results:")
        print(f"  Target: {results['target_url']}")
        print(f"  Score: {results['score']}/100")
        print(f"  Grade: {results['grade']}")
        print(f"  Headers Present: {results['headers_present']}/{results['headers_required']}")

        print(f"\n  Header Results:")
        for header_result in results["header_results"]:
            status = "✓" if header_result["present"] else "✗"
            req = "(required)" if header_result["required"] else "(optional)"
            print(f"    {status} {header_result['header']} {req}")

        if results.get("missing_required"):
            print(f"\n  Missing Required Headers:")
            for header in results["missing_required"]:
                print(f"    • {header}")

        print(f"\n  Recommendations:")
        for rec in results["recommendations"][:3]:
            print(f"    • {rec}")

    except Exception as e:
        print(f"Error running security headers test: {e}")
    finally:
        await client.close()


async def example_full_security_scan():
    """
    Example 7: Run a comprehensive security scan.

    This runs multiple security tests and generates a report.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Full Security Scan")
    print("=" * 60)

    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = SecurityClient(http_client)

    try:
        # Run full security scan
        results = await client.run_full_security_scan(
            target_url="/get", parameters=["id", "search", "name"]
        )

        print(f"\nFull Security Scan Results:")
        print(f"  Target: {results['target_url']}")
        print(f"  Overall Score: {results['overall_score']}/100")
        print(f"  Overall Grade: {results['overall_grade']}")

        # Security headers results
        headers_test = results["tests"].get("security_headers", {})
        if headers_test:
            print(f"\n  Security Headers:")
            print(f"    Score: {headers_test.get('score', 0)}/100")

        # SQL Injection results
        sql_tests = results["tests"].get("sql_injection", [])
        if sql_tests:
            vulnerable = sum(1 for t in sql_tests if t.get("vulnerable"))
            print(f"\n  SQL Injection Tests:")
            print(f"    Total: {len(sql_tests)}")
            print(f"    Vulnerable: {vulnerable}")

        # XSS results
        xss_tests = results["tests"].get("xss", [])
        if xss_tests:
            vulnerable = sum(1 for t in xss_tests if t.get("vulnerable"))
            print(f"\n  XSS Tests:")
            print(f"    Total: {len(xss_tests)}")
            print(f"    Vulnerable: {vulnerable}")

    except Exception as e:
        print(f"Error running full security scan: {e}")
    finally:
        await client.close()


async def main():
    """Run all examples."""
    print("QA-FRAMEWORK: Security Testing Examples")
    print("=" * 60)

    # Run examples
    await example_sql_injection_test()
    await example_xss_test()
    await example_authentication_test()
    await example_common_credentials_test()
    await example_rate_limiting_test()
    await example_security_headers_test()
    await example_full_security_scan()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
