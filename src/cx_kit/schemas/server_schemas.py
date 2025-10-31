# cx-kit/src/cx_kit/schemas/server_schemas.py

"""
Defines the Pydantic models for the Syncropel Communication Protocols.

This module is the single source of truth for the structure of all messages
exchanged between a client (like Syncropel Studio) and the `cx-server`.

It covers:
1. SCP (Syncropel Command Protocol): Messages from Client -> Server.
2. SEP (Syncropel Event Protocol): Messages from Server -> Client.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

# Import the canonical workflow schemas from within the cx-kit SDK
from .workflow import ContextualPage

# ========================================================================
#   SECTION 1: COMMAND PROTOCOL (Client -> Server) - SCP v1.1
# ========================================================================


class ScpMessage(BaseModel):
    """The definitive structure for all client-to-server messages (commands)."""

    trace_id: Union[str, UUID] = Field(
        ..., description="Client-generated ID for the entire user action (trace)."
    )
    type: str = Field(
        ..., description="The command type, using a <NOUN>.<VERB> convention."
    )
    payload: Dict[str, Any] = Field(..., description="The command-specific parameters.")
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: "command_id"
        if field_name == "trace_id"
        else field_name,
    )


# --- SCP Payload Schemas ---


class WorkspaceBrowsePayload(BaseModel):
    path: str = Field("/", description="The logical workspace path to browse.")


class PageLoadPayload(BaseModel):
    page_id: str = Field(..., description="The namespaced ID of the page to load.")


class PageSavePayload(BaseModel):
    uri: str = Field(..., description="The VFS URI of the page to save.")
    content: str = Field(..., description="The full, updated text content of the page.")
    base_version_mtime: Optional[float] = Field(
        None,
        description="The last-modified timestamp of the file when the client loaded it, for conflict detection.",
    )


class BlockRunPayload(BaseModel):
    page_id: str
    block_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    content_override: Optional[str] = Field(
        None, description="The current 'dirty' content from the client's editor."
    )


class PageRunPayload(BaseModel):
    page_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class CommandExecutePayload(BaseModel):
    command_text: str
    page_id: Optional[str] = Field(
        None, description="The ID of the active page, providing CWD context."
    )


class AgentPromptPayload(BaseModel):
    prompt: str
    page_id: Optional[str] = None
    notebook_context_id: Optional[str] = None
    context_paths: Optional[List[str]] = None


# ========================================================================
#   SECTION 2: EVENT PROTOCOL (Server -> Client) - SEP v1.1
# ========================================================================


class SepPayload(BaseModel):
    """The main payload of any server-to-client event."""

    level: Literal["debug", "info", "warn", "error"]
    message: str
    fields: Optional[Dict[str, Any]] = Field(
        None, description="The structured, machine-readable data for the event."
    )
    labels: Dict[str, str] = Field(default_factory=dict)


class SepMessage(BaseModel):
    """The definitive structure for all server-to-client messages (events)."""

    trace_id: Union[str, UUID]
    event_id: Union[str, UUID]
    type: str
    source: str
    timestamp: datetime
    payload: SepPayload
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: "command_id"
        if field_name == "trace_id"
        else "id"
        if field_name == "event_id"
        else field_name,
    )


# --- SEP `fields` Schemas: Core UI & SDUI ---


class SduiPayload(BaseModel):
    """The base schema for any Syncropel Declarative UI (SDUI) component."""

    ui_component: str
    props: Dict[str, Any] = Field(default_factory=dict)


class DataRef(BaseModel):
    """The 'Claim Check' for a large data artifact."""

    artifact_id: str
    renderer_hint: str
    metadata: Optional[Dict[str, Any]] = None
    access_url: str


class BlockOutput(BaseModel):
    """The container for a block's result, implementing the Hybrid Claim Check pattern."""

    inline_data: Optional[SduiPayload] = None
    data_ref: Optional[DataRef] = None


# --- SEP `fields` Schemas: Event-Specific Payloads ---


class SessionStateFields(BaseModel):
    connections: List[Dict[str, str]]
    variables: List[Dict[str, str]]


class CommandResultFields(BaseModel):
    result: Any
    new_session_state: Optional[SessionStateFields] = None


class BlockStatusFields(BaseModel):
    block_id: str
    status: Literal["running", "pending", "skipped"]


class BlockOutputFields(BaseModel):
    block_id: str
    status: Literal["success"]
    duration_ms: int
    output: BlockOutput


class BlockErrorFields(BaseModel):
    block_id: str
    status: Literal["error"]
    duration_ms: int
    error: Dict[str, str] = Field(
        ...,
        description="A structured error object with 'message' and optional 'traceback'.",
    )


class PageLoadedFields(BaseModel):
    uri: str
    content: str
    initial_model: ContextualPage


class PageSavedFields(BaseModel):
    uri: str
    name: str


class AgentSuggestedCommand(BaseModel):
    """A fully-formed SCP message that the agent suggests the client send."""

    trace_id: Union[str, UUID] = Field(..., alias="command_id")
    type: str
    payload: Dict[str, Any]
    model_config = ConfigDict(populate_by_name=True)


class AgentResponseAction(BaseModel):
    """Defines a single, clickable action button presented by the agent."""

    id: str
    label: str
    command: AgentSuggestedCommand


class AgentResponseFields(BaseModel):
    """The definitive structure for the `payload.fields` of an AGENT.RESPONSE event."""

    content: str  # Markdown formatted
    actions: List[AgentResponseAction] = Field(default_factory=list)
