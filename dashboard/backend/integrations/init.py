"""
Integration Hub Initialization

Sets up the Integration Hub and registers default providers.
"""
from .manager import integration_manager
from .jira.client import JiraIntegration
from .zephyr.client import ZephyrIntegration
from .alm.client import ALMIntegration
from .testlink.client import TestLinkIntegration
from .azure_devops.client import AzureDevOpsIntegration


def initialize_integrations():
    """
    Initialize and register default integrations.
    
    This function can be called during application startup to ensure
    all integration providers are properly loaded.
    """
    # Verify all providers are available in the registry
    available_providers = integration_manager.get_available_providers()
    
    print(f"Initialized Integration Hub with {len(available_providers)} providers:")
    for provider in available_providers:
        print(f"  - {provider['display_name']} ({provider['name']})")
        if provider.get('paid'):
            print(f"    ⚠️  Paid tool: {provider.get('estimated_cost')}")
    
    return integration_manager


# Optional: Pre-load commonly used integrations
def preload_common_integrations():
    """
    Pre-load commonly used integrations for faster access.
    
    This is optional and mainly useful for performance optimization
    in high-throughput environments.
    """
    # Currently just verifies that all classes can be imported
    # Actual instances are created on-demand when configured
    pass


# Initialize on import
integration_hub = initialize_integrations()
