# cx-kit/src/cx_kit/schemas/agent.py

"""
Defines the core data structures for the agentic layer of the Syncropel platform.

These schemas are the "nouns" of the agent's world, representing its memory (Beliefs),
its perception of available tools (FunctionSignature), its intentions (ToolCall),
and its observations.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Literal, Type, Union


class FunctionSignature(BaseModel):
    """
    A self-describing schema for a single function advertised by a Capability.
    This is the "tool" that is presented to an LLM.
    """

    name: str = Field(
        ...,
        description="The unique, namespaced function name, e.g., 'syncropel:git.clone_repo'.",
    )
    description: str = Field(
        ...,
        description="A clear, natural language description of what the function does, intended for an LLM.",
    )
    parameters: Type[BaseModel] = Field(
        ...,
        description="A Pydantic model class defining the function's arguments, which will be converted to a JSON Schema for the LLM.",
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)


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
    The generic, in-memory 'working memory' or state of an agentic process.
    This flexible structure can support various reasoning models.
    """

    initial_goal: str

    # The history is a chronological log of thoughts, tool calls, and observations,
    # forming the agent's short-term memory for a given task.
    history: List[Union[Message, Observation, ToolCall]] = Field(default_factory=list)

    # A generic key-value store for structured data extracted during the process.
    facts: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured facts discovered during the process, used for long-term reasoning.",
    )
