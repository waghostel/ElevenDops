"""
Postman Configuration Model

This module defines the PostmanConfig Pydantic model for validating
Postman workspace, collection, and environment configuration.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class PostmanConfig(BaseModel):
    """
    Configuration model for Postman integration.
    
    Attributes:
        workspace_id: Postman workspace UID (24 hex characters)
        collection_id: Postman collection UID (24 hex characters)
        environment_id: Postman environment UID (24 hex characters)
        api_key: ElevenLabs API key for Postman Power
        base_url: Backend base URL (default: http://localhost:8000)
        postman_api_key: Postman API key for direct API access
        test_results: Dictionary to store test results
        metadata: Additional metadata
    """
    
    workspace_id: str = Field(..., description="Postman workspace UID")
    collection_id: str = Field(..., description="Postman collection UID")
    environment_id: str = Field(..., description="Postman environment UID")
    api_key: str = Field(..., description="ElevenLabs API key")
    base_url: str = Field(default="http://localhost:8000", description="Backend base URL")
    postman_api_key: Optional[str] = Field(default=None, description="Postman API key")
    test_results: Dict[str, Any] = Field(default_factory=dict, description="Test results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields
        validate_assignment = True
    
    @validator('workspace_id', 'collection_id', 'environment_id')
    def validate_uid_format(cls, v):
        """Validate UID format (24 hex characters)."""
        if not isinstance(v, str):
            raise ValueError("UID must be a string")
        
        # Allow both 24-char hex format and other valid formats
        if len(v) < 8:
            raise ValueError(f"UID must be at least 8 characters, got {len(v)}")
        
        # Check if it's valid hex or alphanumeric
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(f"UID contains invalid characters: {v}")
        
        return v
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """Validate API key is not empty."""
        if not v or not isinstance(v, str):
            raise ValueError("API key must be a non-empty string")
        if len(v) < 8:
            raise ValueError("API key must be at least 8 characters")
        return v
    
    @validator('base_url')
    def validate_base_url(cls, v):
        """Validate base URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PostmanConfig':
        """Create from dictionary."""
        return cls(**data)


__all__ = ['PostmanConfig']
