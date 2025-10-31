# cx-kit/src/cx_kit/schemas/api_catalog.py

"""
Defines the Pydantic models for the ApiCatalog, also known as a "Blueprint".

A Blueprint is a declarative manifest that describes an external service and,
most importantly, specifies which `Capability` plugin is responsible for
interacting with it.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional


class AuthField(BaseModel):
    """Defines a single field for the interactive connection wizard."""

    name: str = Field(
        ..., description="The key for this field (e.g., 'server', 'api_key')."
    )
    label: str = Field(..., description="The human-friendly prompt for this field.")
    type: Literal["detail", "secret"] = Field(
        ..., description="Determines storage ('detail' is public, 'secret' is private)."
    )
    is_password: bool = Field(
        False, description="If true, the input will be masked in the UI."
    )


class SupportedAuthMethod(BaseModel):
    """Describes a complete authentication method that a blueprint supports."""

    type: str = Field(
        ..., description="A unique identifier for this method (e.g., 'api_key')."
    )
    display_name: str = Field(
        ...,
        description="A human-friendly name for this method (e.g., 'API Key Authentication').",
    )
    fields: List[AuthField] = Field(
        ..., description="A list of fields to collect from the user."
    )


class ApiCatalog(BaseModel):
    """
    The definitive schema for a Blueprint (`blueprint.cx.yaml`).

    It serves as the bridge between a user-defined Connection and the specific
    Capability plugin that knows how to operate it.
    """

    id: str = Field(
        ...,
        description="The unique, namespaced ID of the blueprint (e.g., 'community/github@v1.0').",
    )
    name: str = Field(
        ..., description="A human-readable name for the service (e.g., 'GitHub API')."
    )

    # --- THE CRITICAL CHANGE ---
    # We replace the old, ambiguous `connector_provider_key` with the new, explicit `capability_id`.
    capability_id: str = Field(
        ...,
        description="The unique key of the `BaseCapability` plugin that implements this blueprint (e.g., 'system:rest', 'syncropel:sql-mssql').",
    )

    description: Optional[str] = None
    docs_url: Optional[str] = None
    supported_auth_methods: List[SupportedAuthMethod] = Field(default_factory=list)

    # The `config` block is now a generic container for any capability-specific
    # declarative configuration. This is much more flexible than the old, hardcoded
    # `browse_config`, `oauth_config`, etc.
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="A flexible dictionary for capability-specific configurations (e.g., API endpoints, OAuth URLs, table mappings).",
    )

    # --- Internal fields, populated at runtime by the resolver ---
    schemas_module_path: Optional[str] = Field(
        default=None,
        description="The absolute path to the generated schemas.py file for this blueprint.",
        exclude=True,
    )
