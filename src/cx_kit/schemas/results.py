# cx-kit/src/cx_kit/schemas/results.py

"""
Defines the standard, structured return types for all Capability executions.

The `StepResult` model is the universal "receipt" for any completed computation.
It enforces a clean separation of concerns between the primary data payload that
flows to the next step in a pipeline, and any artifacts (files) that were
created as a side-effect.
"""

from pydantic import BaseModel, Field
from typing import Any, List, Dict


class ArtifactSpec(BaseModel):
    """
    A declarative record of a single file created by a Capability.
    This information is used by the WorkflowEngine to populate the final RunManifest.
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
    """

    data: Any = Field(
        ...,
        description="The primary data payload of the step. This is what gets passed as 'piped_input' to the next step in a workflow.",
    )
    artifacts: List[ArtifactSpec] = Field(
        default_factory=list,
        description="A list of all files that were created as side-effects during the step's execution.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="An open dictionary for the capability to pass additional, non-piped metadata back to the orchestrator.",
    )
