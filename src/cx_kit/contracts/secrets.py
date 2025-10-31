# cx-kit/src/cx_kit/contracts/secrets.py

"""
Defines the base contract for pluggable secrets management providers.

This module provides the `BaseSecretProvider` abstract base class.
Any class that implements this contract can be registered via a
'syncropel.secrets' entry point and be used by the core `SecretService`
to fetch secrets from various backends like local files, environment
variables, or dedicated secret managers (e.g., Vault).
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .config import BaseConfig


class BaseSecretProvider(ABC):
    """
    The abstract contract for all secrets backend providers.

    Each implementation is responsible for retrieving a dictionary of secrets
    from a specific backend, given a path or identifier.
    """

    # The unique key for this provider, e.g., "system:file", "syncropel:vault".
    provider_key: ClassVar[str]

    # A reference to the Pydantic model used to configure this provider.
    # This allows the central ConfigManager to validate the provider's
    # configuration section in the main `config.yaml`.
    ConfigModel: ClassVar[Type["BaseConfig"]]

    def __init__(self, config: "BaseConfig"):
        """
        Initializes the provider with its specific, validated configuration.

        Args:
            config: An instance of the Pydantic model defined in `ConfigModel`.
        """
        self.config = config

    @abstractmethod
    async def get_secrets(self, path: str) -> Dict[str, Any]:
        """
        Retrieves a dictionary of secrets for a given path or identifier.

        Args:
            path: A string identifier for the secret to fetch (e.g., a file path
                  for the file provider, or a Vault path for the Vault provider).

        Returns:
            A dictionary containing the secret key-value pairs.

        Raises:
            FileNotFoundError: If the secret at the specified path cannot be found.
            ConnectionError: If the provider cannot connect to its backend.
            Exception: For any other provider-specific errors.
        """
        raise NotImplementedError
