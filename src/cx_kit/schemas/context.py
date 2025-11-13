# cx-kit/src/cx_kit/schemas/context.py

"""
Defines the RunContext, the central, IMMUTABLE data object providing contextual
information to the WorkflowEngine and Capabilities during execution.
"""

from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional, TYPE_CHECKING
from pathlib import Path

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
    variables: Dict[str, Any] = Field(default_factory=dict)
    connections: Dict[str, Any] = Field(default_factory=dict)

    # Injected SDK Services (transient, not part of the serialized model)
    vfs: "VfsService" = Field(exclude=True)
    secrets: "SecretService" = Field(exclude=True)
    llm: "LlmService" = Field(exclude=True)

    # --- MODIFICATION START ---
    # 1. REMOVED: The obsolete `current_block` field has been deleted.
    #    It was a remnant of the old DAG engine's context model.

    # 2. UPDATED: Switched from deprecated `class Config` to `model_config`.
    #    This aligns with Pydantic v2+ best practices.
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)
    # --- MODIFICATION END ---

    def with_updates(
        self,
        new_variables: Optional[Dict[str, Any]] = None,
        new_connections: Optional[Dict[str, Any]] = None,
    ) -> "RunContext":
        """
        Returns a NEW, updated RunContext instance. This is the primary method for
        propagating state changes immutably.
        """

        # Use a dictionary for updates to avoid deepcopying the entire model.
        update_dict = {}

        if new_variables:
            # Create a new merged dictionary for variables.
            updated_vars = self.variables.copy()
            updated_vars.update(new_variables)
            update_dict["variables"] = updated_vars

        if new_connections:
            # Create a new merged dictionary for connections.
            updated_conns = self.connections.copy()
            updated_conns.update(new_connections)
            update_dict["connections"] = updated_conns

        # `model_copy` is the idiomatic Pydantic v2 method for creating a new
        # instance with updated fields while preserving immutability.
        if not update_dict:
            return self  # Return self if no updates are made.

        return self.model_copy(update=update_dict)

    def resolve_path(self, path_str: str) -> Path:
        """
        Resolves a VFS path string using the full context of the current running flow.
        """
        return self.vfs.resolve_path(path_str, relative_to=self.current_flow_path)
