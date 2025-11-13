# cx-kit/src/cx_kit/contracts/discovery.py

"""
Defines the abstract contract for all pluggable discovery providers.
"""

from abc import ABC, abstractmethod
from typing import List, Any
from ..schemas.discovery import CapabilityDefinition


class BaseDiscoveryProvider(ABC):
    """The contract for a plugin that can discover and parse capability definitions."""

    provider_id: str

    @abstractmethod
    def can_discover(self, source: Any) -> bool:
        """Return True if this provider can handle the given source (e.g., a file path or URL)."""
        raise NotImplementedError

    @abstractmethod
    async def discover(self, source: Any) -> List[CapabilityDefinition]:
        """Parse the source and return a list of standardized capability definitions."""
        raise NotImplementedError
