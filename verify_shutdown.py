#!/usr/bin/env python3
"""
Quick verification script for shutdown module
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.infrastructure.shutdown.models import (
            ShutdownPhase, ShutdownStatus, ResourceType,
            ConnectionInfo, ResourceInfo, ShutdownConfig,
            ShutdownProgress, ShutdownResult
        )
        print("✓ models.py imported successfully")
    except Exception as e:
        print(f"✗ Failed to import models.py: {e}")
        return False
    
    try:
        from src.infrastructure.shutdown.connection_tracker import ConnectionTracker
        print("✓ connection_tracker.py imported successfully")
    except Exception as e:
        print(f"✗ Failed to import connection_tracker.py: {e}")
        return False
    
    try:
        from src.infrastructure.shutdown.shutdown_manager import ShutdownManager
        print("✓ shutdown_manager.py imported successfully")
    except Exception as e:
        print(f"✗ Failed to import shutdown_manager.py: {e}")
        return False
    
    try:
        from src.infrastructure.shutdown.fastapi_integration import (
            ShutdownMiddleware, setup_fastapi_shutdown
        )
        print("✓ fastapi_integration.py imported successfully")
    except Exception as e:
        print(f"✗ Failed to import fastapi_integration.py: {e}")
        return False
    
    try:
        from src.infrastructure.shutdown.standalone import (
            StandaloneShutdown, BackgroundTaskManager
        )
        print("✓ standalone.py imported successfully")
    except Exception as e:
        print(f"✗ Failed to import standalone.py: {e}")
        return False
    
    try:
        from src.infrastructure.shutdown import (
            shutdown_manager, setup_fastapi_shutdown,
            StandaloneShutdown, ResourceType
        )
        print("✓ __init__.py exports working correctly")
    except Exception as e:
        print(f"✗ Failed to import from __init__.py: {e}")
        return False
    
    return True


def test_model_creation():
    """Test creating model instances"""
    print("\nTesting model creation...")
    from datetime import datetime
    from src.infrastructure.shutdown.models import (
        ConnectionInfo, ResourceInfo, ResourceType,
        ShutdownConfig, ShutdownProgress, ShutdownPhase
    )
    
    try:
        # Test ConnectionInfo
        conn = ConnectionInfo(
            connection_id="test_conn",
            resource_type=ResourceType.DATABASE,
            created_at=datetime.now()
        )
        assert conn.connection_id == "test_conn"
        assert conn.is_active == True
        print("✓ ConnectionInfo created successfully")
    except Exception as e:
        print(f"✗ Failed to create ConnectionInfo: {e}")
        return False
    
    try:
        # Test ShutdownConfig
        config = ShutdownConfig(
            graceful_timeout=30.0,
            drain_timeout=10.0
        )
        assert config.graceful_timeout == 30.0
        print("✓ ShutdownConfig created successfully")
    except Exception as e:
        print(f"✗ Failed to create ShutdownConfig: {e}")
        return False
    
    try:
        # Test ShutdownProgress
        progress = ShutdownProgress(phase=ShutdownPhase.INITIATED)
        assert progress.phase == ShutdownPhase.INITIATED
        assert not progress.is_complete
        print("✓ ShutdownProgress created successfully")
    except Exception as e:
        print(f"✗ Failed to create ShutdownProgress: {e}")
        return False
    
    return True


def test_shutdown_manager_basic():
    """Test basic ShutdownManager functionality"""
    print("\nTesting ShutdownManager...")
    from src.infrastructure.shutdown.shutdown_manager import ShutdownManager
    from src.infrastructure.shutdown.models import ResourceType, ShutdownConfig
    from unittest.mock import Mock
    
    # Reset singleton
    ShutdownManager.reset()
    
    try:
        # Create manager
        config = ShutdownConfig(graceful_timeout=5.0)
        manager = ShutdownManager(config)
        print("✓ ShutdownManager created successfully")
    except Exception as e:
        print(f"✗ Failed to create ShutdownManager: {e}")
        return False
    
    try:
        # Register a resource
        mock_resource = Mock()
        mock_resource.close = Mock()
        
        manager.register_resource(
            name="test_resource",
            resource_type=ResourceType.CUSTOM,
            instance=mock_resource,
            close_handler="close"
        )
        
        assert "test_resource" in manager._resources
        print("✓ Resource registered successfully")
    except Exception as e:
        print(f"✗ Failed to register resource: {e}")
        return False
    
    try:
        # Unregister resource
        result = manager.unregister_resource("test_resource")
        assert result == True
        assert "test_resource" not in manager._resources
        print("✓ Resource unregistered successfully")
    except Exception as e:
        print(f"✗ Failed to unregister resource: {e}")
        return False
    
    try:
        # Check initial state
        assert not manager.is_shutting_down()
        print("✓ is_shutting_down() returns False initially")
    except Exception as e:
        print(f"✗ Failed to check shutdown state: {e}")
        return False
    
    # Cleanup
    ShutdownManager.reset()
    
    return True


def test_standalone_shutdown():
    """Test StandaloneShutdown wrapper"""
    print("\nTesting StandaloneShutdown...")
    from src.infrastructure.shutdown.standalone import StandaloneShutdown
    from unittest.mock import Mock
    
    try:
        shutdown = StandaloneShutdown()
        shutdown.setup(install_signal_handlers=False)
        print("✓ StandaloneShutdown created and setup")
    except Exception as e:
        print(f"✗ Failed to create StandaloneShutdown: {e}")
        return False
    
    try:
        # Register resources
        mock_db = Mock()
        mock_redis = Mock()
        
        shutdown.register_database(mock_db)
        shutdown.register_redis(mock_redis)
        
        assert "database" in shutdown.manager._resources
        assert "redis" in shutdown.manager._resources
        print("✓ Resources registered via wrapper")
    except Exception as e:
        print(f"✗ Failed to register resources: {e}")
        return False
    
    try:
        # Check state
        assert not shutdown.is_shutting_down()
        print("✓ is_shutting_down() working")
    except Exception as e:
        print(f"✗ Failed to check state: {e}")
        return False
    
    return True


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Shutdown Module Verification")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Models", test_model_creation()))
    results.append(("ShutdownManager", test_shutdown_manager_basic()))
    results.append(("StandaloneShutdown", test_standalone_shutdown()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All verification tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
