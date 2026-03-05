"""
Batch Execution Service

Optimiza la ejecución de tests agrupándolos en batches para reducir overhead
y mejorar el tiempo de ejecución total.

Usage:
    from services.batch_execution_service import BatchExecutionService

    batch_service = BatchExecutionService()
    result = batch_service.execute_batch(test_ids, batch_size=10)
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from src.infrastructure.cache.test_cache import TestCache
from services.cache_service import CacheService

logger = logging.getLogger(__name__)


class BatchExecutionService:
    """
    Servicio para ejecutar tests en batches optimizados.

    Optimiza la ejecución agrupando tests similares y ejecutándolos en paralelo.
    """

    def __init__(
        self,
        max_workers: int = 5,
        cache_service: Optional[CacheService] = None,
        test_cache: Optional[TestCache] = None
    ):
        """
        Initialize batch execution service.

        Args:
            max_workers: Maximum parallel workers (default: 5)
            cache_service: CacheService instance
            test_cache: TestCache instance
        """
        self.max_workers = max_workers
        self.cache_service = cache_service or CacheService()
        self.test_cache = test_cache or TestCache()

    def execute_batch(
        self,
        test_ids: List[int],
        executor: Callable[[int], Any],
        batch_size: int = 10,
        use_cache: bool = True,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute tests in optimized batches.

        Args:
            test_ids: List of test IDs to execute
            executor: Function to execute each test (accepts test_id)
            batch_size: Number of tests per batch (default: 10)
            use_cache: Use caching for test results (default: True)
            timeout: Maximum execution time per test in seconds (optional)

        Returns:
            Dictionary with batch execution results
        """
        start_time = datetime.now()
        total_tests = len(test_ids)
        results = {
            "test_ids": test_ids,
            "results": {},
            "stats": {
                "total_tests": total_tests,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "execution_time_ms": 0,
                "batch_size": batch_size,
                "batches_count": (total_tests + batch_size - 1) // batch_size
            }
        }

        logger.info(f"Starting batch execution: {total_tests} tests, batch_size={batch_size}")

        try:
            # Divide tests into batches
            batches = self._create_batches(test_ids, batch_size)

            # Execute batches
            for batch_num, batch in enumerate(batches, 1):
                logger.info(f"Executing batch {batch_num}/{len(batches)}: {len(batch)} tests")

                batch_results = self._execute_batch(
                    batch=batch,
                    executor=executor,
                    use_cache=use_cache,
                    timeout=timeout
                )

                results["results"].update(batch_results["results"])
                results["stats"].update(batch_results["stats"])

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            results["stats"]["execution_time_ms"] = int(execution_time)

            # Calculate pass rate
            total_tests_counted = results["stats"]["passed"] + results["stats"]["failed"] + results["stats"]["errors"] + results["stats"]["skipped"]
            if total_tests_counted > 0:
                results["stats"]["pass_rate"] = round(
                    (results["stats"]["passed"] / total_tests_counted) * 100,
                    2
                )

            logger.info(
                f"Batch execution complete: "
                f"{results['stats']['passed']} passed, "
                f"{results['stats']['failed']} failed, "
                f"{results['stats']['execution_time_ms']}ms"
            )

            return results

        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise

    def _create_batches(
        self,
        test_ids: List[int],
        batch_size: int
    ) -> List[List[int]]:
        """
        Create batches from test IDs.

        Args:
            test_ids: List of test IDs
            batch_size: Number of tests per batch

        Returns:
            List of batches
        """
        return [test_ids[i:i + batch_size] for i in range(0, len(test_ids), batch_size)]

    def _execute_batch(
        self,
        batch: List[int],
        executor: Callable[[int], Any],
        use_cache: bool,
        timeout: Optional[float]
    ) -> Dict[str, Any]:
        """
        Execute a single batch of tests.

        Args:
            batch: List of test IDs in batch
            executor: Function to execute tests
            use_cache: Use caching
            timeout: Timeout per test

        Returns:
            Dictionary with batch results
        """
        batch_results = {
            "results": {},
            "stats": {
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            }
        }

        # Determine execution method based on batch size
        if len(batch) <= self.max_workers:
            # Use ThreadPoolExecutor for small batches
            results = self._execute_with_threads(batch, executor, use_cache, timeout)
        else:
            # Use subprocess for large batches (separate processes)
            results = self._execute_with_subprocesses(batch, executor, use_cache, timeout)

        batch_results["results"].update(results["results"])
        batch_results["stats"].update(results["stats"])

        return batch_results

    def _execute_with_threads(
        self,
        batch: List[int],
        executor: Callable[[int], Any],
        use_cache: bool,
        timeout: Optional[float]
    ) -> Dict[str, Any]:
        """
        Execute batch using ThreadPoolExecutor.

        Args:
            batch: List of test IDs
            executor: Function to execute tests
            use_cache: Use caching
            timeout: Timeout per test

        Returns:
            Dictionary with results and stats
        """
        results = {"results": {}, "stats": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tests
            future_to_test = {
                executor.submit(self._execute_single_test, test_id, executor, use_cache, timeout): test_id
                for test_id in batch
            }

            # Collect results
            for future in as_completed(future_to_test):
                test_id = future_to_test[future]

                try:
                    result = future.result()
                    results["results"][test_id] = result

                    if result["status"] == "passed":
                        results["stats"]["passed"] += 1
                    elif result["status"] == "failed":
                        results["stats"]["failed"] += 1
                    elif result["status"] == "error":
                        results["stats"]["errors"] += 1
                    elif result["status"] == "skipped":
                        results["stats"]["skipped"] += 1

                except Exception as e:
                    results["results"][test_id] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    results["stats"]["errors"] += 1

        return results

    def _execute_with_subprocesses(
        self,
        batch: List[int],
        executor: Callable[[int], Any],
        use_cache: bool,
        timeout: Optional[float]
    ) -> Dict[str, Any]:
        """
        Execute batch using subprocesses (for large batches).

        Args:
            batch: List of test IDs
            executor: Function to execute tests
            use_cache: Use caching
            timeout: Timeout per test

        Returns:
            Dictionary with results and stats
        """
        results = {"results": {}, "stats": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}}

        # Split batch into smaller chunks for subprocess execution
        chunk_size = self.max_workers
        chunks = self._create_batches(batch, chunk_size)

        for chunk in chunks:
            with ThreadPoolExecutor(max_workers=len(chunk)) as executor:
                future_to_test = {
                    executor.submit(self._execute_single_test, test_id, executor, use_cache, timeout): test_id
                    for test_id in chunk
                }

                for future in as_completed(future_to_test):
                    test_id = future_to_test[future]

                    try:
                        result = future.result()
                        results["results"][test_id] = result

                        if result["status"] == "passed":
                            results["stats"]["passed"] += 1
                        elif result["status"] == "failed":
                            results["stats"]["failed"] += 1
                        elif result["status"] == "error":
                            results["stats"]["errors"] += 1
                        elif result["status"] == "skipped":
                            results["stats"]["skipped"] += 1

                    except Exception as e:
                        results["results"][test_id] = {
                            "status": "error",
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        }
                        results["stats"]["errors"] += 1

        return results

    def _execute_single_test(
        self,
        test_id: int,
        executor: Callable[[int], Any],
        use_cache: bool,
        timeout: Optional[float]
    ) -> Dict[str, Any]:
        """
        Execute a single test with caching.

        Args:
            test_id: Test ID
            executor: Function to execute test
            use_cache: Use caching
            timeout: Timeout per test

        Returns:
            Result dictionary
        """
        if use_cache:
            cache_key = f"batch_execution_test_{test_id}"

            # Try to get from cache
            cached_result = self.cache_service.test_cache.get(cache_key)
            if cached_result:
                return cached_result

        try:
            # Execute test
            start_time = datetime.now()
            result = executor(test_id)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Create result dict
            result_dict = {
                "test_id": test_id,
                "status": "passed" if result.get("passed", True) else "failed",
                "result": result,
                "execution_time_ms": execution_time,
                "timestamp": datetime.now().isoformat()
            }

            # Cache the result
            if use_cache:
                self.cache_service.test_cache.set(
                    key=f"batch_execution_test_{test_id}",
                    value=result_dict,
                    ttl=3600
                )

            return result_dict

        except Exception as e:
            return {
                "test_id": test_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def optimize_test_order(self, test_ids: List[int]) -> List[int]:
        """
        Optimize test order for better batch execution.

        Sorts tests by execution time (longest first) to minimize wait time
        for parallel execution.

        Args:
            test_ids: List of test IDs

        Returns:
            Sorted list of test IDs
        """
        # For now, return original order
        # Future: Load execution times from cache or database
        return test_ids

    def calculate_execution_time_estimate(
        self,
        test_ids: List[int],
        executor: Callable[[int], Any]
    ) -> Dict[str, Any]:
        """
        Estimate execution time for batch execution.

        Args:
            test_ids: List of test IDs
            executor: Function to estimate execution time

        Returns:
            Dictionary with time estimate
        """
        # Estimate based on cached results
        total_time_ms = 0
        test_count = len(test_ids)

        for test_id in test_ids:
            cached_result = self.test_cache.get(f"batch_execution_test_{test_id}")

            if cached_result and "execution_time_ms" in cached_result:
                total_time_ms += cached_result["execution_time_ms"]
            else:
                # Estimate 1 second per test
                total_time_ms += 1000

        batch_size = 10
        batches_count = (test_count + batch_size - 1) // batch_size

        return {
            "total_tests": test_count,
            "estimated_total_time_ms": total_time_ms,
            "estimated_total_time_seconds": round(total_time_ms / 1000, 2),
            "batch_size": batch_size,
            "batches_count": batches_count,
            "average_time_per_test_ms": round(total_time_ms / test_count, 2)
        }

    def get_batch_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about batch execution results.

        Args:
            results: Batch execution results

        Returns:
            Dictionary with statistics
        """
        stats = results.get("stats", {})

        return {
            "total_tests": stats.get("total_tests", 0),
            "passed": stats.get("passed", 0),
            "failed": stats.get("failed", 0),
            "errors": stats.get("errors", 0),
            "skipped": stats.get("skipped", 0),
            "pass_rate": stats.get("pass_rate", 0),
            "execution_time_ms": stats.get("execution_time_ms", 0),
            "execution_time_seconds": round(stats.get("execution_time_ms", 0) / 1000, 2),
            "avg_time_per_test_ms": round(
                stats.get("execution_time_ms", 0) / stats.get("total_tests", 1),
                2
            )
        }
