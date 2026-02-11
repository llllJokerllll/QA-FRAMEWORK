"""
Performance Testing Example - QA-FRAMEWORK

This example demonstrates how to use the Performance Testing Module
to run load tests and benchmarks against an API.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.adapters.performance import (
    PerformanceClient,
    MetricsCollector,
    BenchmarkRunner,
    LoadTestRunner,
)
from src.adapters.http import HTTPXClient


async def example_load_test():
    """
    Example 1: Run a load test against an API endpoint.

    This will detect the best available load testing tool
    (locust, k6, or Apache Bench) and run the test.
    """
    print("=" * 60)
    print("EXAMPLE 1: Load Testing")
    print("=" * 60)

    client = PerformanceClient(tool="auto")

    try:
        # Run load test
        results = await client.load_test(
            target_url="http://httpbin.org/get", users=10, duration=30, ramp_up=5
        )

        print(f"\nLoad Test Results:")
        print(f"  Tool Used: {results['tool']}")
        print(f"  Target: {results['target_url']}")
        print(f"  Users: {results['users']}")
        print(f"  Duration: {results['duration']}s")
        print(f"  Success: {results['success']}")

        if results.get("results"):
            print(f"\n  Metrics:")
            for key, value in results["results"].items():
                print(f"    {key}: {value}")

    except Exception as e:
        print(f"Error running load test: {e}")
    finally:
        await client.close()


async def example_benchmark():
    """
    Example 2: Run a benchmark test on an HTTP endpoint.

    This measures response times and throughput for a specific
    number of requests.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Benchmark Testing")
    print("=" * 60)

    # Create HTTP client for benchmark
    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = PerformanceClient(http_client=http_client)

    try:
        # Run benchmark
        result = await client.benchmark(target_url="/get", requests=100)

        print(f"\nBenchmark Results:")
        print(f"  Endpoint: {result.name}")
        print(f"  Iterations: {result.iterations}")
        print(f"  Total Time: {result.total_time:.3f}s")
        print(f"  Avg Time: {result.avg_time:.3f}ms")
        print(f"  Min Time: {result.min_time:.3f}ms")
        print(f"  Max Time: {result.max_time:.3f}ms")
        print(f"  Throughput: {result.throughput:.2f} req/s")

        if result.metadata.get("errors", 0) > 0:
            print(f"  Errors: {result.metadata['errors']}")

    except Exception as e:
        print(f"Error running benchmark: {e}")
    finally:
        await client.close()


async def example_stress_test():
    """
    Example 3: Run a stress test with gradually increasing load.

    This helps identify the breaking point of your API.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Stress Testing")
    print("=" * 60)

    client = PerformanceClient(tool="auto")

    try:
        # Run stress test
        results = await client.stress_test(
            target_url="http://httpbin.org/get",
            start_users=5,
            max_users=50,
            step_users=5,
            step_duration=10,
        )

        print(f"\nStress Test Results:")
        print(f"  Max Users Reached: {results['max_users_reached']}")
        print(f"  Break Point: {results.get('break_point', 'N/A')}")
        print(f"  Total Steps: {len(results['steps'])}")

        print(f"\n  Step-by-Step Results:")
        for step in results["steps"]:
            print(f"    {step['users']} users: {'✓' if step['result']['success'] else '✗'}")

    except Exception as e:
        print(f"Error running stress test: {e}")
    finally:
        await client.close()


async def example_metrics_collection():
    """
    Example 4: Direct metrics collection.

    This shows how to use the MetricsCollector directly to
    collect custom performance metrics.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Custom Metrics Collection")
    print("=" * 60)

    collector = MetricsCollector()
    collector.start_collection()

    # Simulate some measurements
    import random

    for i in range(100):
        response_time = random.uniform(50, 500)  # Simulate response times
        collector.record_response_time(response_time)

        # Simulate some errors
        if i % 20 == 0:
            collector.record_error("timeout", "Request timeout")

    # Get metrics
    metrics = collector.get_metrics()

    print(f"\nCollected Metrics:")
    print(f"  Total Requests: {metrics['total_requests']}")
    print(f"  Successful: {metrics['successful_requests']}")
    print(f"  Failed: {metrics['failed_requests']}")
    print(f"  Error Rate: {metrics['error_rate']:.2f}%")
    print(f"  Throughput: {metrics['throughput']:.2f} req/s")
    print(f"\n  Response Times:")
    print(f"    Avg: {metrics['response_times']['avg']}ms")
    print(f"    Min: {metrics['response_times']['min']}ms")
    print(f"    Max: {metrics['response_times']['max']}ms")
    print(f"    P95: {metrics['response_times']['p95']}ms")
    print(f"    P99: {metrics['response_times']['p99']}ms")


async def example_comparison():
    """
    Example 5: Compare different load configurations.

    This runs multiple load tests with different configurations
    and compares the results.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Load Test Comparison")
    print("=" * 60)

    http_client = HTTPXClient(base_url="http://httpbin.org")
    client = PerformanceClient(http_client=http_client)

    try:
        # Define different load configurations
        configs = [
            {"users": 5, "duration": 10, "ramp_up": 2},
            {"users": 10, "duration": 10, "ramp_up": 2},
            {"users": 20, "duration": 10, "ramp_up": 3},
        ]

        # Run comparison
        results = await client.run_comparison(target_url="/get", configs=configs)

        print(f"\nComparison Results:")
        print(f"  Target: {results['target_url']}")
        print(f"  Total Tests: {results['total_tests']}")
        print(f"  Successful: {results['successful_tests']}")
        print(f"  Failed: {results['failed_tests']}")

    except Exception as e:
        print(f"Error running comparison: {e}")
    finally:
        await client.close()


async def main():
    """Run all examples."""
    print("QA-FRAMEWORK: Performance Testing Examples")
    print("=" * 60)

    # Run examples
    await example_load_test()
    await example_benchmark()
    await example_stress_test()
    await example_metrics_collection()
    await example_comparison()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
