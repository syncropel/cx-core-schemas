# cx-kit/src/cx_kit/schemas/context.py

"""
Defines the RunContext, the central data object providing contextual
information to a Capability during a single step's execution.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    # These imports are only for type-hinting the helper methods.
    import pandas as pd
    from ..toolkit.services import VfsService, SecretService, LlmService


class RunContext(BaseModel):
    """
    An immutable data container holding all relevant state and providing
    helper methods for a single step's execution within a workflow.

    This object is the primary way a Capability interacts with the broader
    Syncropel ecosystem during a run.
    """

    # Core Identifiers
    run_id: str = Field(
        ..., description="The unique ID for the entire workflow execution."
    )
    flow_id: str = Field(
        ..., description="The ID of the notebook or flow being executed."
    )

    # Data Flow
    piped_input: Any = Field(
        None,
        description="The primary data output from the previous step in the pipeline.",
    )
    script_input: Dict[str, Any] = Field(
        default_factory=dict,
        description="Global parameters passed to the entire workflow run.",
    )

    # State & History
    steps: Dict[str, Any] = Field(
        default_factory=dict,
        description="A read-only dictionary of the results from previously completed steps.",
    )
    session: Dict[str, Any] = Field(
        default_factory=dict,
        description="A read-only snapshot of the user's session variables.",
    )

    # Path Context (crucial for VFS operations)
    current_flow_path: Optional[Path] = Field(
        None,
        description="The absolute filesystem path of the notebook/flow file being executed.",
    )

    # Injected SDK Services (transient, not serialized)
    # The concrete implementations are provided by the orchestrator at runtime.
    vfs: "VfsService" = Field(..., exclude=True)
    secrets: "SecretService" = Field(..., exclude=True)
    llm: "LlmService" = Field(..., exclude=True)

    # Use ConfigDict for Pydantic v2 to allow arbitrary types and make it immutable.
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    # --- Convenience Helper Methods ---

    def get_piped_dataframe(self) -> "pd.DataFrame":
        """
        Safely ingests the piped_input into a pandas DataFrame, handling
        None, lists of dicts, etc. Lazily imports pandas.
        """
        import pandas as pd

        if self.piped_input is None:
            return pd.DataFrame()
        if isinstance(self.piped_input, list):
            return pd.DataFrame(self.piped_input)
        # Attempt to convert other types, though list of dicts is standard
        return pd.DataFrame([self.piped_input])

    def resolve_path(self, path_str: str) -> Path:
        """
        Resolves a VFS path string (e.g., 'project-asset:...') using the
        full context of the current running flow. Delegates to the injected VFS service.
        """
        # The VFS service will be given the current_flow_path to resolve correctly.
        return self.vfs.resolve_path(path_str, relative_to=self.current_flow_path)
