# cx-kit/src/cx_kit/schemas/vfs.py

"""
Defines the Pydantic models related to the Virtual File System (VFS)
and the structure of the final, auditable Run Manifest.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


class VfsReference(BaseModel):
    """
    A 'Claim Check' or pointer to a large data artifact stored in a VFS
    (e.g., S3, GCS, local file system).

    This allows the `RunContext` to remain lightweight by passing references
    to data instead of the data itself.
    """

    uri: str = Field(
        ...,
        description="The full, unique URI of the artifact in the VFS, e.g., 'vfs://s3-bucket/path/to/data.parquet'.",
    )
    schema_definition: Optional[Dict[str, Any]] = Field(
        None,
        alias="schema",
        description="An optional schema describing the structure of the data.",
    )
    record_count: Optional[int] = Field(
        None, description="The number of records in the dataset, if applicable."
    )
    size_bytes: Optional[int] = Field(
        None, description="The size of the artifact in bytes."
    )

    class Config:
        populate_by_name = True


class ManifestStepResult(BaseModel):
    """
    A record of a single step's execution, specifically for serialization
    within the final RunManifest. It's a subset of the in-memory StepResult.
    """

    step_id: str
    status: str = Field(
        ...,
        description="The final status of the step: 'completed', 'failed', or 'skipped'.",
    )
    summary: str = Field(..., description="A human-readable summary of the outcome.")
    duration_ms: int = Field(..., description="Execution time in milliseconds.")
    cache_key: str = Field(
        ..., description="The deterministic cache key calculated for this step."
    )
    cache_hit: bool = Field(
        ..., description="Whether the result was retrieved from the cache."
    )
    output_hash: Optional[str] = Field(
        None,
        description="A content hash of the step's primary `data` output, pointing to an object in the CAS cache.",
    )


class ManifestArtifact(BaseModel):
    """Metadata for a single artifact produced by a run, for the RunManifest."""

    content_hash: str = Field(
        ..., description="The content hash of the artifact file in the CAS cache."
    )
    mime_type: str
    size_bytes: int
    type: str = Field(
        "primary_output", description="The semantic type of the artifact."
    )
    tags: Dict[str, Any] = Field(default_factory=dict)


class RunManifest(BaseModel):
    """
    The complete, auditable record of a single workflow execution.
    This is the definitive "receipt" that is saved to disk after every run.
    """

    run_id: str
    flow_id: str
    status: str = Field(
        ..., description="The final status of the entire run: 'completed' or 'failed'."
    )
    timestamp_utc: datetime = Field(
        ..., description="The UTC timestamp when the run was initiated."
    )
    duration_total_ms: int = Field(
        ..., description="Total runtime for the whole workflow in milliseconds."
    )
    parameters: Dict[str, Any] = Field(
        ..., description="The input parameters provided for this run."
    )
    steps: List[ManifestStepResult]
    artifacts: Dict[str, ManifestArtifact] = Field(
        default_factory=dict,
        description="A dictionary mapping a user-friendly artifact name (e.g., 'sales_report.xlsx') to its metadata.",
    )
