"""
Example usage of graceful shutdown for QA-FRAMEWORK

This file demonstrates various ways to use the shutdown manager
in different scenarios:
1. FastAPI application
2. Standalone application
3. Background task management
4. Custom resource management
"""

import asyncio
from typing import Optional

# Example 1: FastAPI Application
# ================================

example_fastapi = """
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
import redis.asyncio as aioredis

from src.infrastructure.shutdown import (
    setup_fastapi_shutdown,
    shutdown_manager,
    register_database_connection,
    register_redis_connection,
    ResourceType,
)

# Create FastAPI app
app = FastAPI(title="QA-FRAMEWORK API")

# Setup graceful shutdown (adds middleware and event handlers)
setup_fastapi_shutdown(app)

# Initialize resources
db_engine = create_async_engine("postgresql+asyncpg://...")
redis_client = aioredis.Redis(host="localhost", port=6379)

# Register resources for shutdown
@app.on_event("startup")
async def startup():
    # Register database
    await register_database_connection(db_engine)
    
    # Register Redis
    await register_redis_connection(redis_client)
    
    # Register custom resources
    shutdown_manager.register_resource(
        name="external_api_client",
        resource_type=ResourceType.CUSTOM,
        instance=external_api_client,
        close_handler="close",
        priority=80  # Close before DB and Redis
    )

# Your application routes
@app.get("/api/test-suites")
async def get_test_suites():
    # Requests are automatically tracked by ShutdownMiddleware
    return {"suites": []}

# That's it! Shutdown will automatically:
# 1. Stop accepting new requests
# 2. Wait for in-flight requests to complete
# 3. Close resources in priority order
# 4. Log progress
"""

# Example 2: Standalone Application
# ==================================

example_standalone = """
import asyncio
from sqlalchemy import create_engine
import redis

from src.infrastructure.shutdown import (
    StandaloneShutdown,
    ResourceType,
)

async def main():
    # Create shutdown handler
    shutdown = StandaloneShutdown()
    shutdown.setup()  # Installs signal handlers
    
    # Initialize resources
    db_engine = create_engine("postgresql://...")
    redis_client = redis.Redis(host="localhost", port=6379)
    
    # Register resources
    shutdown.register_database(db_engine)
    shutdown.register_redis(redis_client)
    
    # Register custom resource
    shutdown.register_resource(
        name="worker_pool",
        resource_type=ResourceType.CUSTOM,
        instance=worker_pool,
        close_handler="shutdown",
        priority=50
    )
    
    # Main application loop
    while not shutdown.is_shutting_down():
        # Process work
        await process_tasks()
        await asyncio.sleep(1)
    
    # Wait for cleanup
    await shutdown.wait_and_cleanup()
    print("Application shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
"""

# Example 3: Background Task Management
# ======================================

example_background_tasks = """
import asyncio
from src.infrastructure.shutdown import (
    StandaloneShutdown,
    BackgroundTaskManager,
    ResourceType,
)

async def worker_task(name: str):
    '''Background worker task'''
    while True:
        # Check if shutdown requested
        # Process work items
        await asyncio.sleep(0.1)

async def main():
    # Setup
    shutdown = StandaloneShutdown()
    shutdown.setup()
    
    # Create background task manager
    task_manager = BackgroundTaskManager()
    
    # Start background tasks
    await task_manager.start_task(
        "worker_1",
        lambda: worker_task("worker-1"),
        restart_on_failure=True
    )
    
    await task_manager.start_task(
        "worker_2",
        lambda: worker_task("worker-2"),
        restart_on_failure=True
    )
    
    # Register task manager for cleanup
    shutdown.manager.add_pre_shutdown_hook(
        lambda: task_manager.stop_all(timeout=10.0)
    )
    
    # Main loop
    while not shutdown.is_shutting_down():
        await asyncio.sleep(1)
    
    # Cleanup
    await shutdown.wait_and_cleanup()

if __name__ == "__main__":
    asyncio.run(main())
"""

# Example 4: Context Manager Pattern
# ===================================

example_context_manager = """
from src.infrastructure.shutdown import shutdown_context

async def process_batch():
    with shutdown_context() as shutdown:
        # Setup resources
        shutdown.register_database(db_engine)
        shutdown.register_redis(redis_client)
        
        # Process until shutdown
        while not shutdown.is_shutting_down():
            await process_item()
        
        # Cleanup happens automatically
"""

# Example 5: FastAPI with Lifespan (Modern Pattern)
# =================================================

example_lifespan = """
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.infrastructure.shutdown import create_shutdown_lifespan

# Create lifespan manager
lifespan = create_shutdown_lifespan()

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup
    from src.infrastructure.shutdown import shutdown_manager, ResourceType
    
    # Initialize resources
    db_engine = create_async_engine("postgresql+asyncpg://...")
    redis_client = aioredis.Redis(host="localhost", port=6379)
    
    # Register resources
    shutdown_manager.register_resource(
        "database",
        ResourceType.DATABASE,
        db_engine,
        close_handler="dispose",
        priority=100
    )
    
    shutdown_manager.register_resource(
        "redis",
        ResourceType.REDIS,
        redis_client,
        close_handler="close",
        priority=90
    )
    
    yield
    
    # Shutdown happens automatically via lifespan

app = FastAPI(lifespan=app_lifespan)
"""

# Example 6: Custom Resource with Complex Cleanup
# ===============================================

example_custom_resource = """
from src.infrastructure.shutdown import shutdown_manager, ResourceType

class CustomResource:
    '''Custom resource with complex cleanup'''
    
    def __init__(self):
        self.connections = []
        self.buffers = []
    
    async def graceful_close(self):
        '''Custom close method with complex logic'''
        # Flush buffers
        for buffer in self.buffers:
            await buffer.flush()
        
        # Close connections
        for conn in self.connections:
            await conn.close()
        
        # Cleanup other resources
        await self.cleanup_temp_files()

# Register with custom close handler
resource = CustomResource()
shutdown_manager.register_resource(
    name="custom_resource",
    resource_type=ResourceType.CUSTOM,
    instance=resource,
    close_handler="graceful_close",  # Custom method name
    priority=50
)
"""

# Example 7: Integration with Existing Dashboard
# ==============================================

example_dashboard_integration = """
# In dashboard/backend/main.py

from fastapi import FastAPI
from database import engine  # SQLAlchemy engine
from core.cache import cache_manager  # Redis cache manager
from src.infrastructure.shutdown import (
    setup_fastapi_shutdown,
    shutdown_manager,
    ResourceType,
)

app = FastAPI(title="QA-Framework Dashboard API")

# Setup graceful shutdown
setup_fastapi_shutdown(app)

@app.on_event("startup")
async def startup_event():
    # Existing initialization
    await init_db()
    set_startup_complete()
    
    # Register resources for shutdown
    # Database engine
    shutdown_manager.register_resource(
        name="database_engine",
        resource_type=ResourceType.DATABASE,
        instance=engine,
        close_handler="dispose",
        priority=100
    )
    
    # Redis cache manager (both sync and async clients)
    async_client = await cache_manager.get_async_client()
    shutdown_manager.register_resource(
        name="redis_async",
        resource_type=ResourceType.REDIS,
        instance=async_client,
        close_handler="close",
        priority=90
    )
    
    if cache_manager._sync_client:
        shutdown_manager.register_resource(
            name="redis_sync",
            resource_type=ResourceType.REDIS,
            instance=cache_manager._sync_client,
            close_handler="close",
            priority=90
        )
    
    logger.info("QA-Framework Dashboard initialized with graceful shutdown")

# Rest of your existing code remains the same
"""

# Example 8: Monitoring Shutdown Progress
# =======================================

example_monitoring = """
import asyncio
from src.infrastructure.shutdown import shutdown_manager

async def monitor_shutdown():
    '''Monitor shutdown progress'''
    while shutdown_manager.is_shutting_down():
        progress = shutdown_manager.get_progress()
        
        print(f"Shutdown Phase: {progress.phase.value}")
        print(f"Active Connections: {progress.active_connections}")
        print(f"Drained: {progress.drained_connections}")
        print(f"Resources Closed: {progress.closed_resources}/{progress.total_resources}")
        
        if progress.errors:
            print(f"Errors: {progress.errors}")
        
        if progress.is_complete:
            print(f"Shutdown complete in {progress.duration_seconds:.2f}s")
            break
        
        await asyncio.sleep(0.5)
"""

# Example 9: Testing Shutdown Behavior
# ====================================

example_testing = """
import pytest
from fastapi.testclient import TestClient
from src.infrastructure.shutdown import ShutdownManager

def test_graceful_shutdown():
    '''Test that shutdown completes gracefully'''
    # Reset singleton
    ShutdownManager.reset()
    
    # Create test app
    app = FastAPI()
    setup_fastapi_shutdown(app)
    
    # Register mock resources
    mock_db = Mock()
    mock_db.dispose = Mock()
    
    shutdown_manager.register_resource(
        "db",
        ResourceType.DATABASE,
        mock_db,
        close_handler="dispose"
    )
    
    # Make requests
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    
    # Trigger shutdown
    import asyncio
    result = asyncio.run(shutdown_manager.shutdown(reason="Test"))
    
    # Verify
    assert result.status == ShutdownStatus.SUCCESSFUL
    assert mock_db.dispose.called
    
    # Cleanup
    ShutdownManager.reset()
"""

if __name__ == "__main__":
    print("Graceful Shutdown Examples")
    print("=" * 60)
    print("\n1. FastAPI Application:")
    print(example_fastapi)
    print("\n2. Standalone Application:")
    print(example_standalone)
    print("\n3. Background Task Management:")
    print(example_background_tasks)
    print("\n4. Context Manager Pattern:")
    print(example_context_manager)
    print("\n5. FastAPI with Lifespan:")
    print(example_lifespan)
    print("\n6. Custom Resource:")
    print(example_custom_resource)
    print("\n7. Dashboard Integration:")
    print(example_dashboard_integration)
    print("\n8. Monitoring Progress:")
    print(example_monitoring)
    print("\n9. Testing:")
    print(example_testing)
