from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from .api_catalog import ApiCatalog


class ConnectionBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    api_catalog_id: str
    auth_method_type: str
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Non-sensitive details like server URL."
    )
    tags: List[str] = Field(default_factory=list)


class ConnectionCreate(ConnectionBase):
    # The 'secrets' field has been removed. The frontend will handle it directly with Vault.
    pass


class ConnectionUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    details: Optional[Dict[str, Any]] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)


class Connection(ConnectionBase):
    id: str
    owner_profile_id: Optional[str] = None
    vault_secret_path: Optional[str] = None
    status: str = "untested"
    last_tested_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    catalog: Optional[ApiCatalog] = Field(
        None,
        description="The full ApiCatalog record, embedded for standalone use or fetched from DB.",
    )

    # This hook runs after the model is initialized.
    @model_validator(mode="after")
    def set_default_timestamps(self) -> "Connection":
        """If timestamps are not provided (e.g., from a local file), set them now."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
        return self


class ConnectionCreateResponse(BaseModel):
    connection: Connection = Field(
        description="The created connection metadata record."
    )
    vault_accessor_token: str = Field(
        description="A short-lived, single-use token for the frontend to write the secret to Vault."
    )
    vault_secret_path: str = Field(
        description="The namespaced path in Vault where the frontend should write the secret."
    )
