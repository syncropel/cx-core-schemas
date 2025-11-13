# cx-kit/src/cx_kit/schemas/discovery.py

"""
Defines the standardized data models for the capability discovery process.
All discovery providers must produce `CapabilityDefinition` objects.
"""

from pydantic import BaseModel, Field
from typing import List


class FunctionDefinition(BaseModel):
    """A standardized, serializable representation of a capability's function."""

    name: str
    description: str
    input_schema_json: str  # The full JSON Schema for input, stored as a string.
    output_schema_json: str | None = (
        None  # The full JSON Schema for output, stored as a string.
    )


class CapabilityDefinition(BaseModel):
    """
    The universal, standardized format for a discovered capability's metadata.
    This is the object that gets written to the `registry.sqlite` database.
    """

    id: str = Field(
        ..., description="The unique capability ID, e.g., 'community:spotify'."
    )
    description: str
    runtime: str = Field(
        ..., description="e.g., 'python_class', 'container', 'remote_proxy'."
    )
    entry_point: str = Field(
        ...,
        description="e.g., 'cx_spotify.capability:SpotifyCapability' or a Docker image URI.",
    )
    functions: List[FunctionDefinition]
