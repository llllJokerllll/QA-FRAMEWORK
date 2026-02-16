"""
TestLink Configuration Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class TestLinkConfig(BaseModel):
    """Configuration for TestLink integration"""
    
    server_url: str = Field(
        ...,
        description="TestLink server URL",
        examples=["http://testlink.yourcompany.com/lib/api/xmlrpc/v1/xmlrpc.php"]
    )
    api_key: str = Field(
        ...,
        description="TestLink API key",
        json_schema_extra={"secret": True}
    )
    dev_key: Optional[str] = Field(
        None,
        description="Developer key (optional)",
        json_schema_extra={"secret": True}
    )
    default_project: Optional[str] = Field(
        None,
        description="Default project name"
    )
    
    @field_validator('server_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('server_url must use HTTP or HTTPS')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "server_url": "http://testlink.yourcompany.com/lib/api/xmlrpc/v1/xmlrpc.php",
                "api_key": "your_testlink_api_key_here",
                "default_project": "QA Project"
            }
        }
