# cx-kit/src/cx_kit/schemas/results.py

"""
Defines the standard, structured return types for all Capability executions and
the results of CXQL block evaluations.

This module is CRITICAL to the native CXQL runtime and the client-server architecture.
"""

from pydantic import BaseModel, Field, ConfigDict  # <-- MODIFIED: Import ConfigDict
from typing import Any, List, Dict, Optional


class ArtifactSpec(BaseModel):
    """
    A declarative record of a single file created by a Capability.
    This information is used by the DocumentOrchestrator to populate the final RunManifest.
    """

    path: str = Field(
        ...,
        description="The full, canonical VFS path of the created artifact (e.g., 'file:///path/to/report.xlsx').",
    )
    type: str = Field(
        "primary_output",
        description="The semantic role of the artifact (e.g., 'primary_output', 'log_file', 'visualization').",
    )


class StepResult(BaseModel):
    """
    The standard, structured return object for all `BaseCapability.execute_function` methods.
    It cleanly separates the primary data payload from side-effects.
    """

    data: Any = Field(
        ...,
        description="The primary data payload of the step. This is what flows down the CXQL pipeline.",
    )
    artifacts: List[ArtifactSpec] = Field(
        default_factory=list,
        description="A list of all files created as side-effects during the step's execution.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="An open dictionary for the capability to pass additional, non-piped metadata back to the orchestrator.",
    )


class BlockResult(BaseModel):
    """
    The definitive result of executing a single CXQL code block.

    This object is the primary communication contract between the WorkflowEngine
    and the DocumentOrchestrator. It encapsulates the complete "delta" of changes
    resulting from a block's execution.
    """

    output_value: Optional[Any] = Field(
        None,
        description="The value of the last expression evaluated in the block for inline output.",
    )
    exported_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="A diff of new or updated global variables from a Preamble block.",
    )
    targeted_outputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary mapping a target_id to its renderable value.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="A standard place for interceptors to attach out-of-band execution metadata.",
    )

    # --- MODIFICATION START ---
    # Replaced the deprecated `class Config` with the modern `model_config`.
    model_config = ConfigDict(
        # Allows for complex, non-Pydantic types (like DataFrames) in the output_value
        # before they are serialized by a renderer.
        arbitrary_types_allowed=True
    )
    # --- MODIFICATION END ---
