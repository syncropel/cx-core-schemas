from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional, List


class AuthField(BaseModel):
    """
    Defines a single field required for a connection, providing all the
    metadata needed for a CLI to dynamically and securely prompt for it.
    """

    name: str = Field(
        ...,
        description="The key for this field (e.g., 'server', 'api_key', 'username').",
    )
    label: str = Field(
        ...,
        description="The human-friendly prompt for this field (e.g., 'Server Address', 'API Key').",
    )
    type: Literal["detail", "secret"] = Field(
        ...,
        description="Determines storage. 'detail' goes to the insecure .conn.yaml, 'secret' goes to .secret.env.",
    )
    is_password: bool = Field(
        False,
        description="If true, the interactive CLI prompt will mask the user's input.",
    )


class SupportedAuthMethod(BaseModel):
    """

    Describes a complete, self-contained authentication method that a blueprint
    supports. This is the contract that drives the `cx connection create` command.
    """

    type: str = Field(
        ...,
        description="A unique identifier for this method within the blueprint (e.g., 'credentials', 'api_key').",
    )
    display_name: str = Field(
        ...,
        description="A human-friendly name for this method, shown to the user (e.g., 'Username & Password').",
    )
    fields: List[AuthField] = Field(
        ...,
        description="A list of all the fields that must be collected from the user for this method.",
    )


class ApiCatalogBase(BaseModel):
    """Base fields for an entry in the API service catalog."""

    name: str
    id: str
    description: Optional[str] = None
    category: str = "General"
    icon: Optional[str] = None
    docs_url: Optional[str] = None
    supported_auth_methods: List[SupportedAuthMethod] = Field(default_factory=list)
    primary_api_definition_id: Optional[str] = None  # Should be a string record ID

    connector_provider_key: Optional[str] = Field(
        default=None,
        description="The registration key for the connection strategy (e.g., 'rest-api_key').",
    )
    # This field holds the declarative blueprint for browsing and interaction.
    # We define it as a flexible dictionary.
    browse_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="A declarative blueprint for browsing this service via the VFS.",
    )
    # The blueprint for how to authenticate.
    auth_config: Optional[Dict[str, Any]] = Field(
        default=None, description="A declarative blueprint for handling authentication."
    )
    oauth_config: Optional[Dict[str, Any]] = Field(
        default=None, description="A declarative blueprint for handling OAuth 2.0."
    )
    # The blueprint for how to test the connection.
    test_connection_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration for the 'Test Connection' functionality.",
    )
    # --- Internal fields, populated at runtime by the resolver ---
    source_spec: Optional[Dict[str, Any]] = Field(default=None, exclude=True)
    schemas_module_path: Optional[str] = Field(
        default=None,
        description="The absolute path to the generated schemas.py file for this blueprint.",
        exclude=True,
    )


class ApiCatalog(ApiCatalogBase):
    """The full API Catalog model, including the database ID."""

    id: str
