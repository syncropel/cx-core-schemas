# cx-kit/src/cx_kit/schemas/workflow.py

"""
Defines the core Pydantic models for representing a computational workflow graph.

The central model is the `WorkflowStep`, which represents a single, universal
node in the computation graph (e.g., a block in a notebook). The `ContextualPage`
is the container for a collection of these steps, representing a complete,
executable document like a `.cx.md` file.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class WorkflowStep(BaseModel):
    """
    The definitive schema for a single, executable or static step/block within
    a declarative workflow. This model is the universal "job ticket" that the
    WorkflowEngine passes to a Capability for execution.
    """

    id: str = Field(
        ..., description="The unique identifier for this block within the page."
    )

    name: Optional[str] = Field(
        None, description="A human-readable name for the block."
    )

    # The 'engine' now directly maps to a Capability's ID, making it the primary
    # dispatch key for connection-less operations.
    engine: Optional[str] = Field(
        None,
        description="The capability_id for a connection-less capability (e.g., 'system:python', 'community:dbt').",
    )

    # The `run` block is now a generic dictionary. The responsibility for validating
    # its contents is delegated to the specific Capability that will execute it.
    # The 'action' key within this dict will map to a `FunctionSignature.name`.
    run: Optional[Dict[str, Any]] = Field(
        None,
        description="The declarative payload for this step, defining the function to run and its parameters.",
    )

    content: Optional[str] = Field(
        None,
        description="The source code or text content for the block (e.g., a SQL query or Python script).",
    )

    connection_source: Optional[str] = Field(
        None,
        description="A source identifier for a connection (e.g., 'user:my-db'), used by connection-based capabilities.",
    )

    inputs: List[str] = Field(
        default_factory=list,
        description="A list of dependencies on outputs from other steps, specified as 'step_id.output_name'.",
    )

    outputs: Union[List[str], Dict[str, str], None] = Field(
        None,
        description="Defines the named outputs of this block. A list for a single output, or a dict of name:jmespath pairs for extraction.",
    )

    depends_on: Optional[List[str]] = Field(
        None,
        description="An explicit list of step IDs that must complete before this step can run.",
    )

    if_condition: Optional[str] = Field(
        None,
        alias="if",
        description="A Jinja2 expression that must evaluate to true for the step to run.",
    )

    class Config:
        # Allows `if_condition` to be populated from an `if:` key in YAML/JSON.
        populate_by_name = True


class PageInputParameter(BaseModel):
    """Defines a single expected input parameter for a ContextualPage."""

    description: Optional[str] = None
    type: str = "string"
    required: bool = False
    default: Optional[Any] = None


class ContextualPage(BaseModel):
    """
    The in-memory representation of a complete, executable document, such as a
    `.cx.md` notebook or a `.flow.yaml` file.
    """

    id: Optional[str] = Field(
        None,
        description="The full, namespaced ID of the page (e.g., 'my-project/my-page').",
    )
    name: str = Field(
        ..., description="The primary name/title of the page from the front matter."
    )
    description: Optional[str] = Field(
        None, description="A human-readable description of the page's purpose."
    )

    # The 'session_provider' key is important for stateful workflows (e.g., browser sessions).
    session_provider: Optional[str] = Field(
        None,
        description="The capability_id of a stateful session provider to wrap the execution.",
    )

    inputs: Dict[str, PageInputParameter] = Field(
        default_factory=dict,
        description="A schema defining the expected parameters for this page.",
    )
    blocks: List[WorkflowStep]
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
