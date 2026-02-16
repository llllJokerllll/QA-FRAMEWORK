"""
API Endpoints for Integration Hub

Provides REST API endpoints for managing and using integrations.
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ...integrations.manager import integration_manager
from backend.integrations.base import TestResult, SyncResult
from backend.integrations.base import IntegrationConfig  # Import the base config

router = APIRouter(prefix="/integrations", tags=["integrations"])


class IntegrationConfigRequest(BaseModel):
    """Request model for configuring an integration"""
    provider: str
    config: Dict[str, Any]


class BulkSyncRequest(BaseModel):
    """Request model for bulk synchronization"""
    results: List[TestResult]
    mappings: Dict[str, Dict[str, Any]]


class SyncRequest(BaseModel):
    """Request model for synchronization"""
    results: List[TestResult]
    providers: Optional[List[str]] = None
    project_key: Optional[str] = None
    cycle_name: Optional[str] = None


class TestCaseRequest(BaseModel):
    """Request model for test case operations"""
    name: str
    description: str
    project_key: str
    folder: Optional[str] = None
    labels: Optional[List[str]] = None
    additional_data: Optional[Dict[str, Any]] = None


class BugRequest(BaseModel):
    """Request model for bug operations"""
    title: str
    description: str
    project_key: str
    test_result: Optional[TestResult] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None
    additional_data: Optional[Dict[str, Any]] = None


@router.get("/providers")
async def get_available_providers():
    """
    Get list of all available integration providers.
    
    Returns:
        List of provider information including configuration schema
    """
    try:
        providers = integration_manager.get_available_providers()
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving providers: {str(e)}")


@router.get("/configured")
async def get_configured_providers():
    """
    Get list of currently configured integrations.
    
    Returns:
        List of configured provider status
    """
    try:
        configured = integration_manager.get_configured_providers()
        return {"configured": configured}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving configured providers: {str(e)}")


@router.post("/configure")
async def configure_integration(request: IntegrationConfigRequest):
    """
    Configure an integration provider.
    
    Args:
        request: Configuration request with provider name and config
    
    Returns:
        Success confirmation
    """
    try:
        success = integration_manager.register_integration(
            provider=request.provider,
            config=request.config
        )
        
        if success:
            return {
                "status": "success",
                "provider": request.provider,
                "configured": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to configure integration")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring integration: {str(e)}")


@router.delete("/configure/{provider}")
async def remove_integration(provider: str):
    """
    Remove/unregister an integration.
    
    Args:
        provider: Provider name to remove
    
    Returns:
        Success confirmation
    """
    try:
        success = integration_manager.unregister_integration(provider)
        
        if success:
            return {
                "status": "success",
                "provider": provider,
                "removed": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to remove integration")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing integration: {str(e)}")


@router.post("/{provider}/connect")
async def connect_integration(provider: str):
    """
    Connect to an integration provider.
    
    Args:
        provider: Provider name to connect to
    
    Returns:
        Connection status
    """
    try:
        success = await integration_manager.connect_integration(provider)
        
        return {
            "provider": provider,
            "connected": success
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to integration: {str(e)}")


@router.post("/{provider}/disconnect")
async def disconnect_integration(provider: str):
    """
    Disconnect from an integration provider.
    
    Args:
        provider: Provider name to disconnect from
    
    Returns:
        Disconnection status
    """
    try:
        success = await integration_manager.disconnect_integration(provider)
        
        return {
            "provider": provider,
            "disconnected": success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting from integration: {str(e)}")


@router.get("/{provider}/health")
async def check_integration_health(provider: str):
    """
    Check health status of an integration.
    
    Args:
        provider: Provider name to check
    
    Returns:
        Health status information
    """
    try:
        health = await integration_manager.health_check(provider)
        return {
            "provider": provider,
            "health": health
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking health: {str(e)}")


@router.get("/health/all")
async def check_all_integrations_health():
    """
    Check health status of all configured integrations.
    
    Returns:
        Health status for all integrations
    """
    try:
        health_status = await integration_manager.get_all_health_status()
        return {"health_status": health_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking health: {str(e)}")


@router.post("/sync")
async def sync_results(request: SyncRequest):
    """
    Synchronize test results to one or more integration providers.
    
    Args:
        request: Sync request with results and target providers
    
    Returns:
        Synchronization results per provider
    """
    try:
        results = await integration_manager.sync_test_results(
            results=request.results,
            providers=request.providers,
            project_key=request.project_key,
            cycle_name=request.cycle_name
        )
        
        # Convert SyncResult objects to dictionaries
        result_dict = {}
        for provider, sync_result in results.items():
            result_dict[provider] = {
                "provider": sync_result.provider,
                "success": sync_result.success,
                "synced_count": sync_result.synced_count,
                "failed_count": sync_result.failed_count,
                "errors": sync_result.errors,
                "details": sync_result.details,
                "timestamp": sync_result.timestamp.isoformat()
            }
        
        return {"sync_results": result_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing results: {str(e)}")


@router.post("/sync/bulk")
async def bulk_sync(request: BulkSyncRequest):
    """
    Perform bulk synchronization with different configurations per provider.
    
    Args:
        request: Bulk sync request with results and provider mappings
    
    Returns:
        Bulk synchronization results
    """
    try:
        results = await integration_manager.bulk_sync(
            results=request.results,
            mappings=request.mappings
        )
        
        return {"bulk_sync_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing bulk sync: {str(e)}")


@router.post("/{provider}/test-cases")
async def create_test_case(provider: str, request: TestCaseRequest):
    """
    Create a test case in the specified provider.
    
    Args:
        provider: Provider name
        request: Test case creation request
    
    Returns:
        Created test case information
    """
    try:
        result = await integration_manager.create_test_case(
            provider=provider,
            name=request.name,
            description=request.description,
            project_key=request.project_key,
            folder=request.folder,
            labels=request.labels,
            **(request.additional_data or {})
        )
        
        return {"test_case": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating test case: {str(e)}")


@router.get("/{provider}/test-cases")
async def get_test_cases(
    provider: str,
    project_key: str,
    folder: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get test cases from the specified provider.
    
    Args:
        provider: Provider name
        project_key: Project key to query
        folder: Optional folder/filter
        status: Optional status filter
    
    Returns:
        List of test cases
    """
    try:
        filters = {}
        if status:
            filters["status"] = status
        
        results = await integration_manager.get_test_cases(
            provider=provider,
            project_key=project_key,
            folder=folder,
            filters=filters
        )
        
        return {"test_cases": results}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting test cases: {str(e)}")


@router.post("/{provider}/bugs")
async def create_bug(provider: str, request: BugRequest):
    """
    Create a bug in the specified provider.
    
    Args:
        provider: Provider name
        request: Bug creation request
    
    Returns:
        Created bug information
    """
    try:
        result = await integration_manager.create_bug(
            provider=provider,
            title=request.title,
            description=request.description,
            project_key=request.project_key,
            test_result=request.test_result,
            severity=request.severity,
            priority=request.priority,
            labels=request.labels,
            **(request.additional_data or {})
        )
        
        return {"bug": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bug: {str(e)}")


@router.get("/{provider}/bugs")
async def get_bugs(
    provider: str,
    project_key: str,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None
):
    """
    Get bugs from the specified provider.
    
    Args:
        provider: Provider name
        project_key: Project key to query
        status: Optional status filter
        assigned_to: Optional assignee filter
    
    Returns:
        List of bugs
    """
    try:
        filters = {}
        if status:
            filters["status"] = status
        if assigned_to:
            filters["assigned_to"] = assigned_to
        
        results = await integration_manager.get_bugs(
            provider=provider,
            project_key=project_key,
            status=status,
            filters=filters
        )
        
        return {"bugs": results}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bugs: {str(e)}")


@router.get("/{provider}/projects")
async def get_projects(provider: str):
    """
    Get projects from the specified provider.
    
    Args:
        provider: Provider name
    
    Returns:
        List of projects
    """
    try:
        results = await integration_manager.get_projects(provider)
        return {"projects": results}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting projects: {str(e)}")


# Include this router in your main application
def include_router(app):
    """Helper function to include this router in the main app"""
    app.include_router(router)
