# cx-kit/src/cx_kit/schemas/connection.py

"""
Defines the Pydantic models for a Connection.

A Connection represents a user's configured instance of a service, linking
a specific Blueprint (`ApiCatalog`) with user-provided details and a reference
to their secrets.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from .api_catalog import ApiCatalog  # <-- Import the refactored ApiCatalog


class ConnectionBase(BaseModel):
    """Base fields for a connection configuration file (`.conn.yaml`)."""

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

    # This field links to the blueprint, which in turn specifies the capability.
    api_catalog_id: str = Field(
        ...,
        description="The ID of the blueprint this connection implements (e.g., 'community/github@v1.0').",
    )

    auth_method_type: str = Field(
        ..., description="The 'type' of the `SupportedAuthMethod` used."
    )

    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Non-sensitive configuration details (e.g., server URL, database name).",
    )
    tags: List[str] = Field(default_factory=list)


class Connection(ConnectionBase):
    """
    The full, in-memory representation of a Connection, including runtime data.
    """

    id: str = Field(
        ...,
        description="The unique, user-defined ID for this connection (e.g., 'user:prod-db').",
    )

    # This field is populated at runtime by the CapabilityLoader/Resolver.
    # It contains the full, parsed blueprint.
    catalog: Optional[ApiCatalog] = Field(
        None, description="The full ApiCatalog (Blueprint) record, embedded at runtime."
    )

    # Fields for platform integration (e.g., multi-tenancy, server-side storage)
    owner_profile_id: Optional[str] = None
    vault_secret_path: Optional[str] = None  # Or path in another secrets backend

    # Metadata
    status: str = "untested"
    last_tested_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode="after")
    def set_default_timestamps(self) -> "Connection":
        """Sets creation/update timestamps if they are not provided (e.g., from a local file)."""
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        return self


# These helper models for API create/update operations can remain as they are,
# as they are specific to a potential server-side API for managing connections.
class ConnectionCreate(ConnectionBase):
    pass


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
