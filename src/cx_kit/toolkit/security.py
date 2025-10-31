# cx-kit/src/cx_kit/toolkit/security.py

"""
Provides the security toolkit for the cx-kit SDK.

This module contains helpers that enable capability developers to securely
access and validate secrets required for their operations, without needing
to know the specifics of the underlying secret storage backend.
"""

from typing import Any, Dict, Optional, Type, TYPE_CHECKING
from pydantic import BaseModel, SecretStr

if TYPE_CHECKING:
    from ..schemas.context import RunContext
    from .services import SecretService


class BaseSecretSchema(BaseModel):
    """
    A base class for defining the shape of a capability's required secrets.
    Inheriting from this allows for typed, validated access to secrets.
    """

    pass


class ApiKeySecret(BaseSecretSchema):
    """A common secret schema for simple API key authentication."""

    api_key: SecretStr


class Oauth2ClientSecret(BaseSecretSchema):
    """A common secret schema for OAuth2 client credentials flow."""

    client_id: str
    client_secret: SecretStr


class ConnectionSecrets:
    """
    A secure, on-demand helper for accessing secrets associated with a connection.

    This class acts as a proxy to the injected `SecretService`, providing a
    developer-friendly interface for fetching and validating secrets.
    """

    def __init__(self, context: "RunContext", connection_source_id: str):
        """
        Initializes the secrets helper for a specific connection.

        Args:
            context: The current `RunContext` which contains the `SecretService`.
            connection_source_id: The ID of the connection whose secrets are needed (e.g., 'user:my-db').
        """
        if not context.secrets:
            raise RuntimeError("SecretService not available in the current RunContext.")
        self._secrets_service: "SecretService" = context.secrets
        self._connection_id = connection_source_id
        self._raw_secrets: Optional[Dict[str, Any]] = None

    async def _load_if_needed(self):
        """Loads the secrets from the backend on first access."""
        if self._raw_secrets is None:
            self._raw_secrets = await self._secrets_service.get_all(self._connection_id)

    async def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a single secret value by its key."""
        await self._load_if_needed()
        return self._raw_secrets.get(key, default)

    async def get_all(self) -> Dict[str, Any]:
        """Retrieves the entire dictionary of secrets for the connection."""
        await self._load_if_needed()
        return self._raw_secrets.copy()

    async def parse_as(self, schema: Type[BaseSecretSchema]) -> BaseSecretSchema:
        """
        Validates and parses the raw secrets into a strongly-typed Pydantic model.

        This is the recommended way to consume secrets, as it provides validation
        and leverages Pydantic's `SecretStr` for enhanced security.

        Args:
            schema: The Pydantic model class (inheriting from `BaseSecretSchema`) to validate against.

        Returns:
            A validated instance of the provided schema model.

        Raises:
            pydantic.ValidationError: If the secrets do not match the schema.
        """
        await self._load_if_needed()
        return schema.model_validate(self._raw_secrets)
