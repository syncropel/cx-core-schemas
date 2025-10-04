from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from .connector_script import ScriptInputParameter, ConnectorStep


class ContextualPage(BaseModel):
    """
    The in-memory representation of a complete, executable `.cx.md` document.
    """

    id: Optional[str] = Field(
        None,
        description="The full, namespaced ID of the page (e.g., 'my-project/my-page').",
    )

    name: str = Field(
        ...,
        description="The primary name/title of the Contextual Page, derived from the front matter.",
    )

    description: Optional[str] = Field(
        None, description="A human-readable description of the page's purpose."
    )

    inputs: Dict[str, ScriptInputParameter] = Field(
        default_factory=dict,
        description="Parameters that can be passed to the entire page at runtime, making it a reusable function.",
    )

    blocks: List[ConnectorStep] = Field(
        ..., description="The ordered list of steps/blocks."
    )

    version: str = Field("1.0.0", description="The version of the Contextual Page.")

    author: Optional[str] = Field(
        None, description="The author of the Contextual Page."
    )

    tags: List[str] = Field(
        default_factory=list,
        description="A list of tags for categorization and discovery.",
    )
