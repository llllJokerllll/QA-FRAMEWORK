"""
Azure DevOps Configuration Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class AzureDevOpsConfig(BaseModel):
    """Configuration for Azure DevOps integration"""
    
    organization_url: str = Field(
        ...,
        description="Azure DevOps organization URL",
        examples=["https://dev.azure.com/yourorganization"]
    )
    project_name: str = Field(
        ...,
        description="Azure DevOps project name"
    )
    personal_access_token: str = Field(
        ...,
        description="Personal Access Token with appropriate scopes",
        json_schema_extra={"secret": True}
    )
    area_path: Optional[str] = Field(
        None,
        description="Area path for work items (e.g., 'MyProject\\Area1')"
    )
    iteration_path: Optional[str] = Field(
        None,
        description="Iteration path for work items (e.g., 'MyProject\\Iteration1')"
    )
    
    @field_validator('organization_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith('https://dev.azure.com/'):
            raise ValueError('organization_url must be in format https://dev.azure.com/organization')
        return v.rstrip('/')
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_url": "https://dev.azure.com/yourorganization",
                "project_name": "MyProject",
                "personal_access_token": "your_personal_access_token",
                "area_path": "MyProject\\Area1",
                "iteration_path": "MyProject\\Iteration1"
            }
        }
