#!/usr/bin/env python3
"""
Performance Benchmark Generator for QA-FRAMEWORK Dashboard

This script generates performance benchmarks and reports based on Locust test results.
It can be run after performance tests to create a summary report.
"""

import os
import json
import csv
import glob
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class BenchmarkResult:
    """Performance benchmark result"""

    endpoint: str
    method: str
    requests: int
    failures: int
    median_ms: float
    avg_ms: float
    min_ms: float
    max_ms: float
    p95_ms: float
    p99_ms: float
    rps: float
    error_rate: float
    timestamp: str


@dataclass
class TestSummary:
    """Summary of performance test results"""

    test_type: str
    duration_seconds: int
    total_requests: int
    total_failures: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    error_rate_percent: float
    max_concurrent_users: int
    timestamp: str


class BenchmarkGenerator:
    """Generate performance benchmarks from Locust results"""

    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        self.benchmarks: List[BenchmarkResult] = []
        self.summary: Dict[str, Any] = {}

    def parse_csv_stats(self, csv_file: str) -> List[BenchmarkResult]:
        """Parse Locust CSV statistics file"""
        results = []

        if not os.path.exists(csv_file):
            print(f"Warning: CSV file not found: {csv_file}")
            return results

        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Parse endpoint name to extract method and path
                    name = row.get("Name", "")
                    method = "GET"  # Default
                    endpoint = name

                    # Determine method based on endpoint patterns
                    if any(x in name.lower() for x in ["create", "post", "login"]):
                        method = "POST"
                    elif any(x in name.lower() for x in ["update", "put"]):
                        method = "PUT"
                    elif any(x in name.lower() for x in ["delete"]):
                        method = "DELETE"

                    result = BenchmarkResult(
                        endpoint=endpoint,
                        method=method,
                        requests=int(row.get("Request Count", 0)),
                        failures=int(row.get("Failure Count", 0)),
                        median_ms=float(row.get("Median Response Time", 0)),
                        avg_ms=float(row.get("Average Response Time", 0)),
                        min_ms=float(row.get("Min Response Time", 0)),
                        max_ms=float(row.get("Max Response Time", 0)),
                        p95_ms=float(row.get("95%", 0)),
                        p99_ms=float(row.get("99%", 0)),
                        rps=float(row.get("Requests/s", 0)),
                        error_rate=float(row.get("Failure Count", 0))
                        / max(int(row.get("Request Count", 1)), 1)
                        * 100,
                        timestamp=datetime.now().isoformat(),
                    )
                    results.append(result)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Could not parse row: {e}")
                    continue

        return results

    def generate_benchmarks(self) -> Dict[str, Any]:
        """Generate benchmarks from all result files"""
        # Find all CSV stats files
        csv_files = glob.glob(os.path.join(self.results_dir, "*_stats.csv"))

        if not csv_files:
            print("No CSV result files found. Run Locust tests first.")
            # Return default benchmarks based on expected performance
            return self._generate_default_benchmarks()

        all_results = []
        for csv_file in csv_files:
            print(f"Processing: {csv_file}")
            results = self.parse_csv_stats(csv_file)
            all_results.extend(results)

        if not all_results:
            return self._generate_default_benchmarks()

        # Calculate aggregate statistics
        total_requests = sum(r.requests for r in all_results)
        total_failures = sum(r.failures for r in all_results)
        avg_response = sum(r.avg_ms * r.requests for r in all_results) / max(
            total_requests, 1
        )

        # Sort by p95 for threshold analysis
        sorted_by_p95 = sorted(all_results, key=lambda x: x.p95_ms, reverse=True)

        self.summary = {
            "timestamp": datetime.now().isoformat(),
            "total_requests": total_requests,
            "total_failures": total_failures,
            "error_rate": round(total_failures / max(total_requests, 1) * 100, 2),
            "avg_response_time_ms": round(avg_response, 2),
            "slowest_endpoints": [
                {
                    "endpoint": r.endpoint,
                    "p95_ms": r.p95_ms,
                    "p99_ms": r.p99_ms,
                    "error_rate": round(r.error_rate, 2),
                }
                for r in sorted_by_p95[:5]
            ],
            "all_results": [asdict(r) for r in all_results],
        }

        return self.summary

    def _generate_default_benchmarks(self) -> Dict[str, Any]:
        """Generate default benchmarks based on expected performance"""
        print(
            "Generating default benchmarks based on expected performance thresholds..."
        )

        default_endpoints = [
            {
                "endpoint": "GET /api/v1/dashboard/stats",
                "p50": 120,
                "p95": 350,
                "p99": 650,
                "rps": 25,
            },
            {
                "endpoint": "GET /api/v1/dashboard/trends",
                "p50": 150,
                "p95": 400,
                "p99": 800,
                "rps": 20,
            },
            {
                "endpoint": "GET /api/v1/suites",
                "p50": 100,
                "p95": 300,
                "p99": 550,
                "rps": 30,
            },
            {
                "endpoint": "POST /api/v1/suites",
                "p50": 180,
                "p95": 500,
                "p99": 900,
                "rps": 15,
            },
            {
                "endpoint": "GET /api/v1/cases",
                "p50": 110,
                "p95": 320,
                "p99": 600,
                "rps": 28,
            },
            {
                "endpoint": "POST /api/v1/cases",
                "p50": 160,
                "p95": 480,
                "p99": 850,
                "rps": 18,
            },
            {
                "endpoint": "POST /api/v1/executions",
                "p50": 200,
                "p95": 600,
                "p99": 1100,
                "rps": 12,
            },
            {
                "endpoint": "POST /api/v1/auth/login",
                "p50": 250,
                "p95": 700,
                "p99": 1200,
                "rps": 10,
            },
        ]

        self.summary = {
            "timestamp": datetime.now().isoformat(),
            "note": "Default benchmarks - run tests to generate actual results",
            "total_requests": 0,
            "total_failures": 0,
            "error_rate": 0.0,
            "avg_response_time_ms": 0.0,
            "expected_performance": default_endpoints,
        }

        return self.summary

    def save_benchmarks(self, filename: str = "benchmarks.json"):
        """Save benchmarks to JSON file"""
        output_path = os.path.join(self.results_dir, filename)

        with open(output_path, "w") as f:
            json.dump(self.summary, f, indent=2)

        print(f"Benchmarks saved to: {output_path}")
        return output_path

    def generate_markdown_report(self, filename: str = "benchmarks.md"):
        """Generate markdown report"""
        output_path = os.path.join(self.results_dir, filename)

        with open(output_path, "w") as f:
            f.write("# QA-FRAMEWORK Performance Benchmarks\n\n")
            f.write(f"**Generated:** {self.summary.get('timestamp', 'N/A')}\n\n")

            if "note" in self.summary:
                f.write(f"**Note:** {self.summary['note']}\n\n")

            # Summary statistics
            f.write("## Summary\n\n")
            f.write(
                f"- **Total Requests:** {self.summary.get('total_requests', 0):,}\n"
            )
            f.write(
                f"- **Total Failures:** {self.summary.get('total_failures', 0):,}\n"
            )
            f.write(f"- **Error Rate:** {self.summary.get('error_rate', 0)}%\n")
            f.write(
                f"- **Average Response Time:** {self.summary.get('avg_response_time_ms', 0)}ms\n\n"
            )

            # Performance thresholds
            f.write("## Performance Thresholds\n\n")
            f.write("| Endpoint | p50 (ms) | p95 (ms) | p99 (ms) | RPS | Status |\n")
            f.write("|----------|----------|----------|----------|-----|--------|\n")

            thresholds = {
                "dashboard": {"p95": 400, "p99": 800},
                "suite": {"p95": 600, "p99": 1200},
                "case": {"p95": 600, "p99": 1200},
                "execution": {"p95": 700, "p99": 1400},
                "auth": {"p95": 800, "p99": 1500},
            }

            if "all_results" in self.summary:
                for result in self.summary["all_results"]:
                    endpoint = result.get("endpoint", "N/A")
                    p50 = result.get("median_ms", 0)
                    p95 = result.get("p95_ms", 0)
                    p99 = result.get("p99_ms", 0)
                    rps = result.get("rps", 0)

                    # Determine status
                    status = "✅ Pass"
                    for key, thresh in thresholds.items():
                        if key in endpoint.lower():
                            if p95 > thresh["p95"] or p99 > thresh["p99"]:
                                status = "❌ Fail"
                            break

                    f.write(
                        f"| {endpoint} | {p50:.0f} | {p95:.0f} | {p99:.0f} | {rps:.1f} | {status} |\n"
                    )

            elif "expected_performance" in self.summary:
                f.write("\n### Expected Performance (Default Benchmarks)\n\n")
                for ep in self.summary["expected_performance"]:
                    f.write(
                        f"- **{ep['endpoint']}**: p50={ep['p50']}ms, p95={ep['p95']}ms, p99={ep['p99']}ms, RPS={ep['rps']}\n"
                    )

            # Recommendations
            f.write("\n## Recommendations\n\n")
            if self.summary.get("error_rate", 0) > 1.0:
                f.write(
                    "- ⚠️ **High Error Rate**: Error rate exceeds 1%. Review API stability.\n"
                )
            if (
                "slowest_endpoints" in self.summary
                and self.summary["slowest_endpoints"]
            ):
                f.write(
                    "- 🐌 **Slow Endpoints**: The following endpoints need optimization:\n"
                )
                for ep in self.summary["slowest_endpoints"][:3]:
                    f.write(f"  - {ep['endpoint']}: p95={ep['p95_ms']:.0f}ms\n")

            f.write("\n---\n")
            f.write("*Generated by QA-FRAMEWORK Performance Benchmark Generator*\n")

        print(f"Markdown report saved to: {output_path}")
        return output_path


def main():
    """Main entry point"""
    # Get the results directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "results")

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Generate benchmarks
    generator = BenchmarkGenerator(results_dir)
    generator.generate_benchmarks()

    # Save results
    json_file = generator.save_benchmarks("benchmarks.json")
    md_file = generator.generate_markdown_report("benchmarks.md")

    print("\n" + "=" * 60)
    print("Performance Benchmarks Generated Successfully!")
    print("=" * 60)
    print(f"JSON: {json_file}")
    print(f"Markdown: {md_file}")
    print("\nTo view benchmarks:")
    print(f"  cat {md_file}")
    print("\nTo run performance tests:")
    print("  locust -f locustfile.py --host=http://localhost:8000")


if __name__ == "__main__":
    main()
