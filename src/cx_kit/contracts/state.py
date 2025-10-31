# cx-kit/src/cx_kit/contracts/state.py

"""
Defines the base contract for pluggable state management providers.

This module provides the `BaseStateProvider` abstract base class.
Any class that implements this contract can be registered via a
'syncropel.state_providers' entry point. It defines the standard
interface for creating, reading, updating, and deleting the `RunContext`
for a workflow, enabling backends like in-memory dictionaries, Redis,
or a file-based system.
"""

from abc import ABC, abstractmethod
from typing import ClassVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .config import BaseConfig
    from ..schemas.context import RunContext
    from ..schemas.results import StepResult


class BaseStateProvider(ABC):
    """
    The abstract contract for all RunContext persistence backends.
    """

    # The unique key for this provider, e.g., "system:memory", "syncropel:redis".
    provider_key: ClassVar[str]

    # A reference to the Pydantic model used to configure this provider.
    ConfigModel: ClassVar[Type["BaseConfig"]]

    def __init__(self, config: "BaseConfig"):
        """
        Initializes the provider with its specific, validated configuration.
        """
        self.config = config

    @abstractmethod
    async def create(self, initial_context: "RunContext") -> str:
        """
        Saves a new `RunContext` at the beginning of a workflow and returns
        its unique `run_id`.

        Args:
            initial_context: The initial state of the RunContext.

        Returns:
            The `run_id` for the newly created context.
        """
        raise NotImplementedError

    @abstractmethod
    async def get(self, run_id: str) -> "RunContext":
        """
        Retrieves a `RunContext` by its unique `run_id`.

        Args:
            run_id: The ID of the run to retrieve.

        Returns:
            The deserialized RunContext object.

        Raises:
            KeyError: If no context for the given run_id is found.
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, context: "RunContext"):
        """
        Updates or overwrites an entire `RunContext` in the state backend.

        Args:
            context: The `RunContext` object to save. It must have a `run_id`.
        """
        raise NotImplementedError

    @abstractmethod
    async def add_step_result(self, run_id: str, step_id: str, result: "StepResult"):
        """
        Atomically appends or updates a single step's result within a stored
        `RunContext`. This can be more efficient than a full save.

        Args:
            run_id: The ID of the run to update.
            step_id: The ID of the step whose result is being added.
            result: The `StepResult` object to add.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, run_id: str):
        """
        Removes a `RunContext` from the state backend, typically after a
        workflow has completed or failed.

        Args:
            run_id: The ID of the run to delete.
        """
        raise NotImplementedError
