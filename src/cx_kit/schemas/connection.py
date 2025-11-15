# cx-kit/src/cx_kit/schemas/connection.py

"""
Defines the Pydantic models for Connections, both for static configuration
and for runtime execution specifications.
"""

from __future__ import annotations
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

# --- MODIFIED: Import Blueprint instead of the legacy ApiCatalog ---
from .blueprint import Blueprint


# ==============================================================================
# SECTION 1: STATIC CONNECTION CONFIGURATION
# These models represent a connection as it is configured and saved by a user.
# ==============================================================================


class ConnectionBase(BaseModel):
    """Base fields for a connection configuration file (`.conn.yaml`)."""

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    # This field links to the blueprint, which in turn specifies the capability.
    blueprint_id: str = Field(
        ...,
        description="The ID of the blueprint this connection implements (e.g., 'community/sql-mssql').",
    )

    auth_method_type: str = Field(
        ...,
        description="The 'type' of the `SupportedAuthMethod` used from the blueprint.",
    )

    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Non-sensitive configuration details (e.g., server URL, database name).",
    )
    tags: List[str] = Field(default_factory=list)


class Connection(ConnectionBase):
    """
    The full, in-memory representation of a saved Connection, including runtime metadata.
    This model is typically used by management commands like `cx connection list`.
    """

    id: str = Field(
        ...,
        description="The unique, user-defined ID for this connection (e.g., 'user:prod-db').",
    )

    # This field is populated at runtime by a resolver.
    blueprint: Optional[Blueprint] = Field(
        None, description="The full Blueprint record, embedded at runtime."
    )

    # Path to the secrets in a secure backend (e.g., a file in ~/.cx/secrets).
    secret_ref: str = Field(
        ..., description="A reference to the stored secrets for this connection."
    )

    # Metadata
    status: str = "untested"
    last_tested_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode="after")
    def set_default_timestamps(self) -> "Connection":
        """Sets creation/update timestamps if they are not provided."""
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        return self


# ==============================================================================
# SECTION 2: RUNTIME CONNECTION SPECIFICATION
# This model is the in-memory "passport" used by the engine during execution.
# ==============================================================================


class ConnectionSpec(BaseModel):
    """
    An immutable runtime object representing a fully resolved connection for a single call.

    This object is created by `sys.connect()` and stored in a variable. When
    used in a function call (e.g., `$db.query(...)`), the Evaluator uses the
    information within this spec to load the correct capability and provide it
    with the necessary configuration to execute the request.
    """

    blueprint_id: str = Field(
        ..., description="The ID of the blueprint this connection implements."
    )
    capability_id: str = Field(
        ..., description="The ID of the capability that will execute the call."
    )

    details: Dict[str, Any] = Field(
        default_factory=dict, description="Non-sensitive connection details."
    )
    secrets: Dict[str, Any] = Field(
        default_factory=dict,
        description="The resolved secret values for this specific call.",
    )
    alias: str = Field(
        ..., description="The alias this connection is known by in the current scope."
    )

    # Use ConfigDict for immutability and to allow complex types if needed in the future.
    model_config = ConfigDict(frozen=True)
