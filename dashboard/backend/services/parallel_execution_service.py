"""
Parallel Execution Service - Optimized

Optimiza la ejecución paralela de tests con worker pools eficientes
y gestión de recursos compartidos.

Usage:
    from services.parallel_execution_service import ParallelExecutionService

    parallel_service = ParallelExecutionService(max_workers=10)
    result = parallel_service.execute_parallel(test_ids)
"""

import logging
import threading
from typing import Any, Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from queue import Queue
from datetime import datetime, timedelta

from src.infrastructure.cache.test_cache import TestCache
from services.cache_service import CacheService
from services.batch_execution_service import BatchExecutionService

logger = logging.getLogger(__name__)


class SharedResourceManager:
    """
    Manager for shared resources across parallel executions.

    Handles:
    - Database connection pooling
    - API client instances
    - File handles
    - Custom resources
    """

    def __init__(self):
        """Initialize shared resource manager."""
        self._resources = {}
        self._locks = {}
        self._counters = {}

    def acquire(self, resource_type: str, resource_id: str = None) -> Any:
        """
        Acquire a shared resource.

        Args:
            resource_type: Type of resource
            resource_id: Specific resource ID (optional)

        Returns:
            Resource instance
        """
        if resource_type not in self._resources:
            self._resources[resource_type] = {}
            self._locks[resource_type] = threading.Lock()

        key = f"{resource_type}:{resource_id}" if resource_id else resource_type

        with self._locks[resource_type]:
            if key not in self._resources[resource_type]:
                # Create new resource
                resource = self._create_resource(resource_type, resource_id)
                self._resources[resource_type][key] = resource

            # Increment usage counter
            if key not in self._counters:
                self._counters[key] = 0
            self._counters[key] += 1

            logger.debug(f"Acquired resource: {key}, usage: {self._counters[key]}")
            return self._resources[resource_type][key]

    def release(self, resource_type: str, resource_id: str = None):
        """
        Release a shared resource.

        Args:
            resource_type: Type of resource
            resource_id: Specific resource ID (optional)
        """
        key = f"{resource_type}:{resource_id}" if resource_id else resource_type

        # Check if resource type exists
        if resource_type not in self._locks:
            logger.debug(f"Resource type {resource_type} not found, nothing to release")
            return

        with self._locks[resource_type]:
            if key in self._counters:
                self._counters[key] -= 1

                if self._counters[key] <= 0:
                    # Clean up resource if no longer needed
                    if key in self._resources[resource_type]:
                        del self._resources[resource_type][key]
                    del self._counters[key]
                else:
                    logger.debug(f"Released resource: {key}, usage: {self._counters[key]}")

    def get_usage(self, resource_type: str) -> Dict[str, int]:
        """
        Get resource usage statistics.

        Args:
            resource_type: Type of resource

        Returns:
            Dictionary with resource usage
        """
        with self._locks[resource_type]:
            return {
                key: count
                for key, count in self._counters.items()
                if key.startswith(resource_type)
            }

    def _create_resource(self, resource_type: str, resource_id: str = None) -> Any:
        """Create a new resource instance (override in subclass)."""
        if resource_type == "database":
            return self._create_database_connection()
        elif resource_type == "api_client":
            return self._create_api_client()
        else:
            raise ValueError(f"Unknown resource type: {resource_type}")

    def _create_database_connection(self) -> Any:
        """Create a new database connection (placeholder)."""
        # In production: create actual connection
        return {"type": "database", "connected": True}

    def _create_api_client(self) -> Any:
        """Create a new API client (placeholder)."""
        # In production: create actual client
        return {"type": "api_client", "initialized": True}


class ParallelExecutionService:
    """
    Optimized parallel execution service with efficient worker pools.

    Features:
    - Adaptive worker pool sizing
    - Shared resource management
    - Load balancing
    - Graceful error handling
    """

    def __init__(
        self,
        max_workers: int = 10,
        cache_service: Optional[CacheService] = None,
        test_cache: Optional[TestCache] = None,
        shared_resources: bool = True
    ):
        """
        Initialize parallel execution service.

        Args:
            max_workers: Maximum number of parallel workers (default: 10)
            cache_service: CacheService instance
            test_cache: TestCache instance
            shared_resources: Use shared resource management (default: True)
        """
        self.max_workers = max_workers
        self.cache_service = cache_service or CacheService()
        self.test_cache = test_cache or TestCache()
        self.shared_resources = shared_resources
        self.resource_manager = SharedResourceManager() if shared_resources else None

        # Performance tracking
        self._execution_times = []
        self._resource_usage_history = []

    def execute_parallel(
        self,
        test_ids: List[int],
        executor: Callable[[int], Any],
        use_cache: bool = True,
        adaptive_workers: bool = True
    ) -> Dict[str, Any]:
        """
        Execute tests in parallel with optimized worker pool.

        Args:
            test_ids: List of test IDs to execute
            executor: Function to execute each test
            use_cache: Use caching for test results
            adaptive_workers: Adjust worker count based on system resources

        Returns:
            Dictionary with parallel execution results
        """
        start_time = datetime.now()

        # Adjust worker count if adaptive
        workers = self._adjust_worker_count(adaptive_workers) if adaptive_workers else self.max_workers

        logger.info(f"Starting parallel execution: {len(test_ids)} tests, {workers} workers")

        results = {
            "test_ids": test_ids,
            "results": {},
            "stats": {
                "total_tests": len(test_ids),
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "execution_time_ms": 0,
                "worker_count": workers,
                "worker_pool_efficiency": 0
            }
        }

        try:
            # Use ThreadPoolExecutor for CPU-bound tasks
            with ThreadPoolExecutor(max_workers=workers) as thread_executor:
                # Submit all tests
                future_to_test = {
                    thread_executor.submit(
                        self._execute_single_test,
                        test_id,
                        executor,
                        use_cache
                    ): test_id
                    for test_id in test_ids
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

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            results["stats"]["execution_time_ms"] = int(execution_time)

            # Calculate worker pool efficiency
            results["stats"]["worker_pool_efficiency"] = self._calculate_efficiency(results["stats"]["passed"], results["stats"]["failed"])

            logger.info(
                f"Parallel execution complete: "
                f"{results['stats']['passed']} passed, "
                f"{results['stats']['failed']} failed, "
                f"{results['stats']['execution_time_ms']}ms"
            )

            return results

        except Exception as e:
            logger.error(f"Parallel execution failed: {e}")
            raise

    def _adjust_worker_count(self, adaptive: bool) -> int:
        """
        Adjust worker count based on system resources.

        Args:
            adaptive: Whether to adapt worker count

        Returns:
            Adjusted worker count
        """
        if not adaptive:
            return self.max_workers

        # Simplified adaptive logic
        # In production: consider CPU count, memory, system load
        return self.max_workers

    def _calculate_efficiency(self, passed: int, failed: int) -> float:
        """
        Calculate worker pool efficiency.

        Args:
            passed: Number of passed tests
            failed: Number of failed tests

        Returns:
            Efficiency score (0-100)
        """
        total = passed + failed
        if total == 0:
            return 0.0

        # Simple efficiency metric
        return round((passed / total) * 100, 2)

    def _execute_single_test(
        self,
        test_id: int,
        executor: Callable[[int], Any],
        use_cache: bool
    ) -> Dict[str, Any]:
        """
        Execute a single test with caching.

        Args:
            test_id: Test ID
            executor: Function to execute test
            use_cache: Use caching

        Returns:
            Result dictionary
        """
        # Include executor in cache key to differentiate between different executors
        executor_id = id(executor) if executor else 0
        cache_key = f"parallel_execution_test_{test_id}_{executor_id}"

        if use_cache:
            # Try to get from cache
            cached_result = self.test_cache.get(cache_key)
            if cached_result:
                return cached_result

        try:
            # Execute test
            start_time = datetime.now()
            result = executor(test_id)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Determine status based on result
            status = "passed"
            if isinstance(result, dict):
                if result.get("error"):
                    status = "error"
                elif result.get("passed") is False:
                    status = "failed"
                elif result.get("status") == "skipped":
                    status = "skipped"
                elif result.get("passed") is True:
                    status = "passed"

            # Create result dict
            result_dict = {
                "test_id": test_id,
                "status": status,
                "result": result,
                "execution_time_ms": execution_time,
                "timestamp": datetime.now().isoformat()
            }

            # Cache the result
            if use_cache:
                self.test_cache.set(
                    key=cache_key,
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

    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "max_workers": self.max_workers,
            "shared_resources_enabled": self.shared_resources,
            "resource_types": self.resource_manager.get_usage("database") if self.shared_resources else {},
            "total_executions": len(self._execution_times)
        }

    def get_shared_resource_usage(self, resource_type: str) -> Dict[str, int]:
        """
        Get shared resource usage.

        Args:
            resource_type: Type of resource

        Returns:
            Dictionary with resource usage
        """
        if self.shared_resources:
            return self.resource_manager.get_usage(resource_type)
        return {}

    def cleanup_resources(self):
        """Clean up all shared resources."""
        if self.shared_resources and self.resource_manager:
            # Release all resources
            for resource_type in list(self.resource_manager._resources.keys()):
                for resource_id in list(self.resource_manager._resources[resource_type].keys()):
                    self.resource_manager.release(resource_type, resource_id)

            logger.info("All shared resources cleaned up")

    def __del__(self):
        """Clean up resources on service destruction."""
        self.cleanup_resources()


class LoadBalancer:
    """
    Simple load balancer for distributing tests across workers.

    Implements:
    - Round-robin distribution
    - Load-aware distribution
    - Worker priority
    """

    def __init__(self, worker_count: int):
        """
        Initialize load balancer.

        Args:
            worker_count: Number of workers
        """
        self.worker_count = worker_count
        self._current_worker = 0

    def distribute(self, items: List[Any], load_aware: bool = False) -> List[List[Any]]:
        """
        Distribute items across workers.

        Args:
            items: List of items to distribute
            load_aware: Use load-aware distribution

        Returns:
            List of items per worker
        """
        if load_aware:
            return self._distribute_load_aware(items)
        return self._distribute_round_robin(items)

    def _distribute_round_robin(self, items: List[Any]) -> List[List[Any]]:
        """Distribute using round-robin."""
        result = [[] for _ in range(self.worker_count)]

        for i, item in enumerate(items):
            worker_idx = i % self.worker_count
            result[worker_idx].append(item)

        return result

    def _distribute_load_aware(self, items: List[Any]) -> List[List[Any]]:
        """
        Distribute using load-aware strategy.

        Assigns more items to less loaded workers.
        """
        result = [[] for _ in range(self.worker_count)]
        worker_loads = [0] * self.worker_count

        for item in items:
            # Find least loaded worker
            least_loaded = min(range(self.worker_count), key=lambda x: worker_loads[x])

            result[least_loaded].append(item)
            worker_loads[least_loaded] += 1

        return result
