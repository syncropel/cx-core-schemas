# cx-kit/src/cx_kit/schemas/context.py

"""
Defines the RunContext, the central, IMMUTABLE data object providing contextual
information to the WorkflowEngine and Capabilities during execution.
"""

from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional, TYPE_CHECKING
from pathlib import Path

# Import the new ConnectionSpec for type hinting
from .connection import ConnectionSpec

if TYPE_CHECKING:
    from ..toolkit.services import VfsService, SecretService, LlmService


class RunContext(BaseModel):
    """
    An immutable data container holding all relevant state for a given point
    in a workflow execution.

    This object is passed down the execution chain. Components do not modify it;
    instead, they return new objects or values, and the orchestrator creates a
    new, updated context for the next step.
    """

    # Core Identifiers for tracing and asset resolution
    run_id: str
    flow_id: str

    # Paths and Filesystem Context
    cx_home: Path
    current_flow_path: Optional[Path] = None

    # State & Scope
    variables: Dict[str, Any] = Field(
        default_factory=dict, description="The current variable scope."
    )
    connections: Dict[str, Any] = Field(
        default_factory=dict,
        description="A cache of initialized singleton capability instances.",
    )

    # This field holds the specific connection details for the *current* stateful function call.
    # It is excluded from serialization as it is a short-lived, runtime-only object.
    active_connection: Optional[ConnectionSpec] = Field(None, exclude=True)

    # Injected SDK Services (transient, not part of the serialized model)
    vfs: "VfsService" = Field(exclude=True)
    secrets: "SecretService" = Field(exclude=True)
    llm: "LlmService" = Field(exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    def with_updates(
        self,
        new_variables: Optional[Dict[str, Any]] = None,
        active_connection: Optional[ConnectionSpec] = None,
    ) -> "RunContext":
        """
        Returns a NEW, updated RunContext instance. This is the primary method for
        propagating state changes immutably.

        The Evaluator uses this to create a short-lived context with an
        `active_connection` for a single stateful function call.
        """
        update_dict = {}

        if new_variables:
            updated_vars = self.variables.copy()
            updated_vars.update(new_variables)
            update_dict["variables"] = updated_vars

        # --- THIS IS THE CRITICAL ADDITION ---
        # Allow the `active_connection` to be set for the new context.
        # Note: Pydantic's `model_copy` handles `None` correctly, so we can
        # set it directly.
        if active_connection is not None:
            update_dict["active_connection"] = active_connection

        if not update_dict:
            return self

        # `model_copy` is the idiomatic Pydantic v2 method for creating a new
        # instance with updated fields while preserving immutability.
        return self.model_copy(update=update_dict)

    def resolve_path(self, path_str: str) -> Path:
        """
        Resolves a VFS path string using the full context of the current running flow.
        """
        # Delegate path resolution to the VFS service, providing it with the
        # necessary context from this RunContext instance.
        return self.vfs.resolve_path(path_str, relative_to=self.current_flow_path)
