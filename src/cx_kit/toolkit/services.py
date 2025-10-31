# cx-kit/src/cx_kit/toolkit/services.py

"""
Defines the abstract interfaces (Protocols) for the SDK services that the
core orchestrator (`cx-shell`) injects into every `BaseCapability`.

By coding against these stable interfaces, capability developers are completely
decoupled from the orchestrator's internal implementation details.
"""

from typing import Any, Dict, List, Protocol, Type, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    # Use TYPE_CHECKING to avoid circular dependency issues at runtime
    # while providing full type hints for static analysis.
    from pydantic import BaseModel
    from ..schemas.context import RunContext
    from ..schemas.workflow import WorkflowStep


class LlmService(Protocol):
    """
    An interface to the platform's centrally-managed Large Language Model client.

    This allows any capability to leverage AI without managing API keys or clients.
    The orchestrator ensures the correct, user-configured model is used.
    """

    async def prompt(
        self,
        context: "RunContext",
        messages: List[Dict],
        response_model: Type["BaseModel"] | None = None,
    ) -> Any:
        """
        Sends a prompt to the user's configured default LLM.

        Args:
            context: The current RunContext for observability and context.
            messages: A list of messages in the OpenAI chat completion format.
            response_model: An optional Pydantic model to structure the LLM's response.

        Returns:
            The raw string or a validated Pydantic model instance.
        """
        ...


class SecretService(Protocol):
    """
    An interface to the platform's secrets management backend.

    This provides a secure, unified way for capabilities to access secrets
    from various providers (e.g., local files, Vault) as configured by the user.
    """

    async def get(self, context: "RunContext", path: str, key: str) -> str | None:
        """Retrieves a single secret value."""
        ...

    async def get_all(self, context: "RunContext", path: str) -> Dict[str, str]:
        """Retrieves all secrets from a given path as a dictionary."""
        ...


class VfsService(Protocol):
    """
    An interface to the Syncropel Virtual File System (VFS).

    Provides capabilities with a unified, context-aware way to read and write
    files and data artifacts, abstracting away the underlying storage (local, S3, etc.).
    """

    def resolve_path(self, path_str: str, relative_to: Path | None = None) -> Path:
        """
        Resolves a VFS path string (e.g., 'project-asset:data.csv') to an
        absolute filesystem path, using the provided context.
        """
        ...

    async def read_bytes(self, path: Path) -> bytes:
        """Reads the raw bytes of a file from the VFS."""
        ...

    async def write_bytes(self, path: Path, content: bytes) -> str:
        """Writes bytes to a file in the VFS and returns its canonical URI."""
        ...


class WorkflowService(Protocol):
    """

    An interface providing a "callback" to the core WorkflowEngine.

    This allows a meta-strategy (like a renderer) to request the execution
    of another capability as part of its own logic.
    """

    async def execute_step(self, context: "RunContext", step: "WorkflowStep") -> Any:
        """
        Requests that the orchestrator execute a dynamically constructed step.
        """
        ...
