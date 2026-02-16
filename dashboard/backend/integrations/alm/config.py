"""
ALM Configuration Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ALMConfig(BaseModel):
    """Configuration for HP ALM / OpenText ALM integration"""
    
    base_url: str = Field(
        ...,
        description="ALM server URL",
        examples=["https://alm.yourcompany.com/qcbin"]
    )
    username: str = Field(
        ...,
        description="ALM username"
    )
    password: str = Field(
        ...,
        description="ALM password",
        json_schema_extra={"secret": True}
    )
    domain: str = Field(
        "DEFAULT",
        description="ALM domain"
    )
    project: str = Field(
        ...,
        description="ALM project name"
    )
    
    @field_validator('base_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith('http'):
            raise ValueError('base_url must use HTTP or HTTPS')
        return v.rstrip('/')
    
    class Config:
        json_schema_extra = {
            "example": {
                "base_url": "https://alm.yourcompany.com/qcbin",
                "username": "qa_user",
                "password": "your_password",
                "domain": "DEFAULT",
                "project": "QA_PROJECT"
            }
        }
