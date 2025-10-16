# /cx-core-schemas/src/cx_core_schemas/server_schemas.py

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from .notebook import ContextualPage

# ========================================================================
#   SECTION 1: COMMAND PROTOCOL (Client -> Server) - SCP v1.0
# ========================================================================
# This section defines the structure of all commands sent FROM the client
# TO the server via the WebSocket. This is the Syncropel Command Protocol.


class ScpPayloadBase(BaseModel):
    """A base model for all incoming command payloads."""

    pass


class SessionInitPayload(ScpPayloadBase):
    """Payload for the SESSION.INIT command, sent on initial connection."""

    pass


class WorkspaceBrowsePayload(ScpPayloadBase):
    """Payload for the WORKSPACE.BROWSE command."""

    path: str = Field("/", description="The logical workspace path to browse.")


class PageLoadPayload(ScpPayloadBase):
    """Payload for the PAGE.LOAD command."""

    page_id: str = Field(..., description="The namespaced ID of the page to load.")


class PageSavePayload(ScpPayloadBase):
    """Payload for the PAGE.SAVE command."""

    page: ContextualPage = Field(..., description="The complete, updated page model.")


class BlockRunPayload(ScpPayloadBase):
    """Payload for the BLOCK.RUN command, the primary execution trigger."""

    page_id: str = Field(..., description="The ID of the page containing the block.")
    block_id: str = Field(..., description="The ID of the block to execute.")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Page-level parameters for the run.",
    )
    content_override: Optional[str] = Field(
        None,
        description="The current content from the client's editor, to override the saved version.",
    )


class CommandExecutePayload(ScpPayloadBase):
    """Payload for the COMMAND.EXECUTE command, used by the integrated terminal."""

    command_text: str = Field(..., description="The raw cx-shell command to execute.")


class ScpMessage(BaseModel):
    """The definitive structure for all client-to-server messages."""

    trace_id: Union[str, UUID] = Field(
        ...,
        alias="command_id",
        description="Client-generated ID for the entire user action (trace). Aliased as command_id for backward compatibility.",
    )
    type: str = Field(
        ..., description="The command type, using a <NOUN>.<VERB> convention."
    )
    payload: Dict[str, Any] = Field(..., description="The command-specific parameters.")

    class Config:
        populate_by_name = True


# ========================================================================
#   SECTION 2: EVENT PROTOCOL (Server -> Client) - SEP v1.0
# ========================================================================
# This section defines the structure of all events sent FROM the server
# TO the client. This is the Syncropel Event Protocol.


class SduiPayload(BaseModel):
    """The base schema for any Syncropel Declarative UI (SDUI) component."""

    ui_component: str = Field(
        ..., description="The name of the component to render (e.g., 'table', 'card')."
    )
    props: Dict[str, Any] = Field(
        default_factory=dict,
        description="The properties to pass to the React component.",
    )


class DataRef(BaseModel):
    """
    The 'Claim Check' for a large data artifact, providing a reference
    to the data instead of embedding it directly in the event.
    """

    artifact_id: str = Field(
        ...,
        description="The content-hash ID (e.g., 'sha256:...') of the data in the Fabric.",
    )
    renderer_hint: str = Field(
        ...,
        description="A hint for the UI on which component to use (e.g., 'table', 'image').",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Metadata about the artifact, like record count or file size."
    )
    access_url: str = Field(
        ...,
        description="The fully-qualified, secure URL to retrieve the artifact content.",
    )


class BlockOutput(BaseModel):
    """
    The container for a block's result, implementing the Hybrid Claim Check pattern.
    Exactly one of `inline_data` or `data_ref` must be present.
    """

    inline_data: Optional[SduiPayload] = Field(
        None, description="The full SDUI payload, embedded for small results."
    )
    data_ref: Optional[DataRef] = Field(
        None, description="A reference to the artifact for large results."
    )


class SessionStateFields(BaseModel):
    """Fields describing the current state of a user's session."""

    connections: List[Dict[str, str]]
    variables: List[Dict[str, str]]


class CommandResultFields(BaseModel):
    """Fields for a simple, synchronous COMMAND.RESULT event."""

    result: Any
    new_session_state: SessionStateFields


class BlockStatusFields(BaseModel):
    """Fields for a BLOCK.STATUS event."""

    block_id: str
    status: Literal["running", "pending", "skipped"]


class BlockOutputFields(BaseModel):
    """Fields for a BLOCK.OUTPUT event."""

    block_id: str
    status: Literal["success"]
    duration_ms: int
    output: BlockOutput


class BlockErrorFields(BaseModel):
    """Fields for a BLOCK.ERROR event."""

    block_id: str
    status: Literal["error"]
    duration_ms: int
    error: Dict[str, str] = Field(..., description="A structured error object.")


class SepPayload(BaseModel):
    """The main payload of any server-to-client event."""

    level: Literal["debug", "info", "warn", "error"]
    message: str
    fields: Optional[Dict[str, Any]] = Field(
        None,
        description="The structured, machine-readable data specific to the event type.",
    )
    labels: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Filterable key-value tags. Recommended: component, run_id.",
    )


class SepMessage(BaseModel):
    """The definitive structure for all server-to-client messages."""

    trace_id: Union[str, UUID] = Field(
        ...,
        alias="command_id",
        description="The ID of the client command that initiated this event or event stream.",
    )
    event_id: Union[str, UUID] = Field(
        ..., alias="id", description="A unique UUID for this specific event."
    )
    type: str = Field(
        ..., description="The event type, using a <NOUN>.<VERB> convention."
    )
    source: str = Field(..., description="A URI-like identifier of the event's origin.")
    timestamp: datetime = Field(
        ..., description="ISO 8601 timestamp of when the event occurred."
    )
    payload: SepPayload = Field(..., description="The content of the event.")

    class Config:
        populate_by_name = True
