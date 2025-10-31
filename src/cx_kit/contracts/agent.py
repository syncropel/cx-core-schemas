from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, ClassVar, Dict, List, Type, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..schemas.agent import Beliefs, FunctionSignature, Message, ToolCall
    from ..toolkit.services import LlmService
    from .config import BaseConfig


class BaseAgentSkill(ABC):
    """
    The contract for a pluggable, specialized cognitive function (e.g., planning, analysis).
    Skills are the building blocks used by a ReasoningFlow.
    """

    skill_id: ClassVar[str]
    ConfigModel: ClassVar[Type["BaseConfig"]]

    def __init__(self, config: "BaseConfig", llm_service: "LlmService"):
        self.config = config
        self.llm = llm_service

    @abstractmethod
    async def invoke(self, beliefs: "Beliefs", **kwargs) -> Any:
        """The main entry point for the skill."""
        raise NotImplementedError


class BaseReasoningFlow(ABC):
    """The contract for a complete, pluggable reasoning process (a 'brain')."""

    flow_id: ClassVar[str]

    def __init__(self, services: Dict[str, Any]):
        """Injects SDK services, like a loader for AgentSkills."""
        self._skill_loader = services.get("skill_loader")

    @abstractmethod
    async def run(
        self, initial_goal: str, tools: List["FunctionSignature"]
    ) -> AsyncIterator[Union["Message", "ToolCall"]]:
        """The main async generator that drives the agent's thought process."""
        yield
