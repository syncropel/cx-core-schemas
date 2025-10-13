# /cx-core-schemas/src/cx_core_schemas/project.py

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# --- Schemas for cx.project.yaml (The Human-Authored Manifest) ---


class EnvironmentSpec(BaseModel):
    """Defines system-level dependencies managed by the Nix engine."""

    packages: List[str] = Field(
        default_factory=list,
        description="A list of system-level packages to be provisioned by Nix (e.g., 'python@3.12', 'nodejs@20').",
    )


class PythonToolsSpec(BaseModel):
    """Defines Python-specific tooling and dependencies."""

    requirements: Optional[str] = Field(
        None,
        description="Path to a pip-style requirements.txt file, relative to the project root.",
    )


class NodeToolsSpec(BaseModel):
    """(Future) Defines Node.js-specific tooling and dependencies."""

    package_json: Optional[str] = Field(
        None, description="Path to a package.json file, relative to the project root."
    )


class ToolingSpec(BaseModel):
    """Container for all language-specific tooling configurations."""

    python: Optional[PythonToolsSpec] = None
    node: Optional[NodeToolsSpec] = None


class SyncropelSpec(BaseModel):
    """Defines Syncropel-native dependencies for the project."""

    apps: Dict[str, str] = Field(
        default_factory=dict,
        description="A mapping of Syncropel application names to their version constraints (e.g., 'system/toolkit': '^1.0.0').",
    )
    overrides: Dict[str, str] = Field(
        default_factory=dict,
        description="A mapping of a system asset's logical ID to a local file path, for customization.",
    )


class ProjectManifest(BaseModel):
    """
    The definitive schema for the cx.project.yaml file.
    This is the universal, human-authored manifest for a Syncropel project.
    """

    environment: Optional[EnvironmentSpec] = None
    tools: Optional[ToolingSpec] = None
    syncropel: Optional[SyncropelSpec] = None


# --- Schemas for cx.lock.json (The Machine-Generated Lockfile) ---


class LockedPackage(BaseModel):
    """Defines the exact, resolved state of a single Syncropel application package."""

    version: str = Field(
        ..., description="The exact, pinned version of the application (e.g., '1.1.0')."
    )
    source: str = Field(
        ..., description="The source of the package (e.g., 'registry', 'local')."
    )
    integrity: str = Field(
        ...,
        description="The checksum (e.g., 'sha256-...') of the downloaded artifact for security.",
    )
    dependencies: Dict[str, str] = Field(
        default_factory=dict,
        description="(Future) A mapping of transitive Syncropel application dependencies.",
    )


class Lockfile(BaseModel):
    """
    The definitive schema for the cx.lock.json file.
    This file guarantees deterministic, reproducible Syncropel environments.
    """

    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Metadata about the lockfile, such as the lockfile format version.",
    )
    packages: Dict[str, LockedPackage] = Field(
        ...,
        description="A dictionary mapping application names to their locked definitions.",
    )
