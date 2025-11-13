# cx-kit/src/cx_kit/schemas/agent.py

"""
Defines the core data structures for the agentic layer of the Syncropel platform.

These schemas are the "nouns" of the agent's world, representing its memory (Beliefs),
its perception of available tools (FunctionSignature), its intentions (ToolCall),
and its observations.
"""

from pydantic import BaseModel, Field, ConfigDict  # <-- MODIFIED: Import ConfigDict
from typing import Any, Dict, List, Literal, Optional, Type, Union


class FunctionSignature(BaseModel):
    """
    A self-describing schema for a single function advertised by a Capability.
    This is the "tool" that is presented to an LLM.
    """

    name: str = Field(
        ...,
        description="The unique, namespaced function name, e.g., 'system:fs.read'.",
    )
    description: str = Field(
        ...,
        description="A clear, natural language description of what the function does, intended for an LLM.",
    )
    input_schema: Type[BaseModel] = Field(
        ...,
        alias="parameters",
        description="A Pydantic model defining the function's input arguments.",
    )
    output_schema: Optional[Type[BaseModel]] = Field(
        None,
        description="An optional Pydantic model describing the function's output.",
    )

    # --- MODIFICATION START ---
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Necessary to allow `Type[BaseModel]`
        populate_by_name=True,  # Allows 'parameters' to populate 'input_schema'
    )
    # --- MODIFICATION END ---


class ToolCall(BaseModel):
    """Represents an agent's decision to call a specific function with validated arguments."""

    function_name: str
    parameters: Dict[str, Any]


class Message(BaseModel):
    """A single turn in an agentic conversation or thought process."""

    role: Literal["user", "assistant", "system", "tool"]
    content: str


class Observation(BaseModel):
    """The structured result of a tool execution, to be added to the agent's memory."""

    tool_name: str
    tool_input: Dict
    output: Any
    status: Literal["success", "failure"]


class Beliefs(BaseModel):
    """
    The in-memory 'working memory' or state of an agentic process.
    """

    initial_goal: str
    history: List[Union[Message, Observation, ToolCall]] = Field(default_factory=list)
    facts: Dict[str, Any] = Field(default_factory=dict)
