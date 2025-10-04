from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


class VfsNodeMetadata(BaseModel):
    """
    Metadata about a VFS node, indicating its capabilities and state.
    """

    can_write: bool = Field(
        ..., description="Whether the current user can write to this node."
    )
    is_versioned: bool = Field(
        ..., description="Whether the node is under version control (e.g., Git)."
    )
    etag: str = Field(
        ...,
        description="The entity tag for this version of the file (e.g., a Git commit hash or an S3 ETag).",
    )
    last_modified: datetime = Field(
        ...,
        description="The last modified timestamp of the file.",
    )


class VfsFileContentResponse(BaseModel):
    """
    The data contract for the response from the /vfs/open endpoint.
    Provides everything the frontend needs to render and manage a file.
    """

    path: str = Field(..., description="The full VFS path of the file that was opened.")
    content: str = Field(
        ..., description="The content of the file, typically as a string."
    )
    mime_type: str = Field(
        ...,
        alias="mimeType",
        description="The MIME type of the file, e.g., 'text/markdown'.",
    )
    # last_modified: datetime = Field(
    #     ...,
    #     alias="lastModified",
    #     description="The last modified timestamp of the file.",
    # )
    size: int = Field(..., ge=0, description="The size of the file in bytes.")
    metadata: VfsNodeMetadata
    session_token: Optional[str] = Field(
        default=None,
        description="A short-lived JWT for write operations if the file is writable and versioned.",
    )

    model_config = {
        "populate_by_name": True,  # Allows using both snake_case and alias (camelCase)
    }


class StepResult(BaseModel):
    """A record of a single step's execution within a run."""

    step_id: str
    status: str  # "completed", "failed", "skipped"
    summary: str
    cache_key: str
    cache_hit: bool
    output_hash: Optional[str] = None  # SHA256 hash of the raw data output


class Artifact(BaseModel):
    """Metadata for a single artifact produced by a run."""

    content_hash: str  # SHA256 hash pointing to the data in the cache
    mime_type: str
    size_bytes: int
    tags: Dict[str, Any] = Field(default_factory=dict)


class RunManifest(BaseModel):
    """The complete, auditable record of a single command execution."""

    run_id: str
    flow_id: str
    status: str
    timestamp_utc: datetime
    parameters: Dict[str, Any]
    steps: List[StepResult]
    artifacts: Dict[str, Artifact] = Field(default_factory=dict)
