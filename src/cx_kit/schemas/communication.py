# cx-kit/src/cx_kit/schemas/communication.py

"""
Definitive Pydantic models for the Syncropel Communication Protocols (SCP & SEP).
These models are the Python representation of the canonical TypeScript contracts.
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, Literal, Optional
from datetime import datetime, timezone


from pydantic import BaseModel, Field

from .document import ParsedDocument

# ==============================================================================
# Base Event & Command Schemas (Envelopes)
# ==============================================================================


class ServerEventPayload(BaseModel):
    level: Literal["debug", "info", "warn", "error"]
    message: str
    fields: Optional[Dict[str, Any]] = None


class ServerEvent(BaseModel):
    trace_id: uuid.UUID
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    type: str
    source: str = "/cx-server"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: ServerEventPayload


class ClientCommand(BaseModel):
    trace_id: uuid.UUID
    type: str
    payload: Dict[str, Any]


# ==============================================================================
# SCP Payload Schemas (Client -> Server)
# ==============================================================================


class PageLoadPayload(BaseModel):
    page_id: str


class BlockRunPayload(BaseModel):
    page_id: str
    block_id: str
    content_override: Optional[str] = None


# ==============================================================================
# SEP `fields` Schemas (Server -> Client)
# ==============================================================================


class BlockOutput(BaseModel):
    """Represents a renderable output, either as inline SDUI or a data reference."""

    inline_data: Optional[Dict[str, Any]] = None  # This would be a ComponentNode model
    data_ref: Optional[Dict[str, Any]] = None  # This would be a DataRef model


class BlockOutputFields(BaseModel):
    """The 'Render-Delta' payload for a successful block execution."""

    block_id: str
    status: Literal["success"]
    duration_ms: int
    inline_output: Optional[BlockOutput] = None
    targeted_outputs: Optional[Dict[str, BlockOutput]] = None
    context_updates: Optional[Dict[str, Any]] = None


class PageLoadedFields(BaseModel):
    page_id: str
    content: str
    document: ParsedDocument
