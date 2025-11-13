# cx-kit/src/cx_kit/schemas/project.py

"""
Defines the canonical Pydantic models for the Syncropel ecosystem's core
structural assets: Projects, Documents, and the deprecated legacy Block model.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    ConfigDict,
)  # <-- MODIFIED: Import ConfigDict

# ==============================================================================
# SECTION 1: DOCUMENT & LEGACY BLOCK SCHEMAS
# ==============================================================================


class Block(BaseModel):
    """
    DEPRECATED: The legacy schema for a single, executable block.
    This model is the universal "job ticket" for the deprecated DAG-based engine.
    The new native runtime uses the `CodeBlock` and `MarkdownBlock` schemas.
    """

    id: str = Field(..., description="The unique identifier for this block.")
    name: Optional[str] = Field(
        None, description="A human-readable name for the block."
    )
    engine: Optional[str] = Field(
        None, description="The capability_id for a connection-less capability."
    )
    connection: Optional[str] = Field(
        None, description="The ID of a connection to use for this block."
    )
    run: Optional[Dict[str, Any]] = Field(
        None, description="The declarative payload defining the function to run."
    )
    content: Optional[str] = Field(
        None, description="The source code or text content for the block."
    )
    inputs: List[str] = Field(
        default_factory=list,
        description="Data dependencies on outputs from other blocks.",
    )
    outputs: Union[List[str], Dict[str, str], None] = Field(
        None, description="Named outputs of this block."
    )
    depends_on: Optional[List[str]] = Field(
        None, description="Explicit execution order dependencies."
    )
    if_condition: Optional[str] = Field(
        None, alias="if", description="A Jinja2 expression for conditional execution."
    )

    # PrivateAttrs are instance attributes not part of the Pydantic schema.
    # They are used for internal framework metadata.
    _shell_directives: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _session_update: Dict[str, Any] = PrivateAttr(default_factory=dict)

    # --- MODIFICATION START ---
    model_config = ConfigDict(
        populate_by_name=True,  # Allows using the alias 'if' for 'if_condition'
        extra="allow",  # Allows private attributes like `_shell_directives`
    )
    # --- MODIFICATION END ---


class DocumentInput(BaseModel):
    """Defines a single expected input parameter for a Document."""

    description: Optional[str] = None
    type: str = "string"
    required: bool = False
    default: Optional[Any] = None


class Document(BaseModel):
    """
    DEPRECATED: The in-memory representation for the DAG-based engine.
    """

    id: str
    name: str
    description: Optional[str] = None
    inputs: Dict[str, DocumentInput] = Field(default_factory=dict)
    blocks: List[Block]
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


# ==============================================================================
# SECTION 2: PROJECT MANIFEST & LOCKFILE SCHEMAS
# ==============================================================================


# These schemas are still relevant and do not require ConfigDict as they have no special config.
class EnvironmentSpec(BaseModel):
    """Defines system-level dependencies for a project's environment."""

    packages: List[str] = Field(default_factory=list)


class PythonToolsSpec(BaseModel):
    """Defines Python-specific tooling and dependencies."""

    requirements: Optional[str] = Field(
        None, description="Path to a requirements.txt file."
    )


class ToolingSpec(BaseModel):
    """Container for all language-specific tooling configurations."""

    python: Optional[PythonToolsSpec] = None


class SyncropelSpec(BaseModel):
    """Defines Syncropel-native dependencies for the project."""

    apps: Dict[str, str] = Field(default_factory=dict)


class ProjectManifest(BaseModel):
    """The definitive schema for the `cx.project.yaml` file."""

    environment: Optional[EnvironmentSpec] = None
    tools: Optional[ToolingSpec] = None
    syncropel: Optional[SyncropelSpec] = None


class LockedPackage(BaseModel):
    """Defines the exact, resolved state of a single Syncropel application package."""

    version: str
    source: str
    integrity: str


class Lockfile(BaseModel):
    """The definitive schema for the `cx.lock.json` file."""

    metadata: Dict[str, str] = Field(default_factory=dict)
    packages: Dict[str, LockedPackage]
