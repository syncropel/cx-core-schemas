# cx-kit/src/cx_kit/toolkit/agentic.py

"""
Provides the agentic toolkit for the cx-kit SDK.

This module contains high-level, reusable components for building and running
agentic processes. It includes the `ToolRegistry` for discovering capabilities
and the `AgentOrchestrator` for executing pluggable reasoning flows.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from ..contracts.capability import BaseCapability
    from ..contracts.agent import BaseReasoningFlow
    from ..schemas.agent import FunctionSignature

logger = structlog.get_logger(__name__)


class ToolRegistry:
    """
    A discoverable registry of all tools (functions) available in the environment,
    provided by all installed `BaseCapability` plugins.
    """

    def __init__(self, capability_loader):
        """
        Args:
            capability_loader: An instance of the orchestrator's CapabilityLoader.
        """
        self._loader = capability_loader
        self._tool_schemas: Optional[List["FunctionSignature"]] = None
        self._tool_map: Optional[Dict[str, "BaseCapability"]] = None

    def get_all_schemas(self) -> List["FunctionSignature"]:
        """
        Discovers all capabilities and aggregates their function signatures.
        This is the list of tools that gets passed to an agent.
        """
        if self._tool_schemas is None:
            self._tool_schemas = []
            self._tool_map = {}
            # The capability_loader is provided by the cx-shell orchestrator
            all_capabilities = self._loader.discover_plugins()
            for key, entry_point in all_capabilities.items():
                try:
                    capability_instance = self._loader.load_strategy(key)
                    functions = capability_instance.get_functions()
                    for func_sig in functions:
                        # Store which capability provides which function
                        self._tool_map[func_sig.name] = capability_instance
                    self._tool_schemas.extend(functions)
                except Exception as e:
                    logger.warning(
                        "Failed to load functions from capability.",
                        capability_id=key,
                        error=str(e),
                    )

            logger.info("Tool discovery complete.", tool_count=len(self._tool_schemas))

        return self._tool_schemas

    def get_capability_for_function(self, function_name: str) -> "BaseCapability":
        """Finds the capability instance responsible for executing a given function."""
        if self._tool_map is None:
            self.get_all_schemas()  # Ensure discovery has run

        capability = self._tool_map.get(function_name)
        if not capability:
            raise NameError(
                f"No installed capability provides a function named '{function_name}'."
            )
        return capability


class AgentOrchestrator:
    """
    A generic, reusable orchestrator for running agentic workflows.
    This class lives in the SDK so that any application can host agents.
    """

    def __init__(self, services: Dict[str, Any]):
        """
        Initializes the orchestrator with injected services from the host application.
        """
        self.tool_registry = services.get("tool_registry")
        self.workflow_engine = services.get("workflow_engine")
        self._skill_loader = services.get("skill_loader")  # A loader for agent skills
        self._reasoning_flow_loader = services.get(
            "reasoning_flow_loader"
        )  # A loader for reasoning flows

    async def run(self, reasoning_flow_id: str, initial_goal: str, **kwargs) -> Any:
        """
        Executes an agentic process based on a named reasoning flow.

        This method acts as the main loop, mediating between the pluggable
        ReasoningFlow, the ToolRegistry, and the core WorkflowEngine.
        """
        reasoning_flow: "BaseReasoningFlow" = self._reasoning_flow_loader.load(
            reasoning_flow_id
        )
        available_tools = self.tool_registry.get_all_schemas()

        # The reasoning_flow is an async generator that yields its desired actions.
        async for action in reasoning_flow.run(initial_goal, available_tools):
            # The host application (e.g., cx-shell) would then handle these actions:
            # - If action is a Message, display it to the user.
            # - If action is a ToolCall, prompt for confirmation and then
            #   use the WorkflowEngine to execute it.
            # - Feed the Observation back into the reasoning_flow.
            pass  # Placeholder for host application's handling logic.
