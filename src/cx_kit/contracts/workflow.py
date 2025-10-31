# cx-kit/src/cx_kit/contracts/workflow.py

"""
Defines the contracts for the Interception & Extension Protocol (IEP).

These abstract base classes allow developers to build plugins that hook into
the lifecycle of workflow and step execution, enabling cross-cutting concerns
like security, auditing, and caching.
"""

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from ..schemas.context import RunContext
    from ..schemas.workflow import ContextualPage, WorkflowStep


class BaseWorkflowInterceptor(ABC):
    """
    The contract for a plugin that intercepts an ENTIRE workflow run.
    This is the highest level of computational interception.
    """

    priority: ClassVar[int] = 100

    @abstractmethod
    async def intercept(
        self,
        context: "RunContext",
        page: "ContextualPage",
        next_handler: Callable[[], Awaitable[Any]],
    ) -> Any:
        """
        Intercepts a full workflow run. Must call `await next_handler()`
        to proceed with the actual execution.
        """
        raise NotImplementedError


class BaseWorkflowStepInterceptor(ABC):
    """
    The contract for a plugin that intercepts a SINGLE workflow step's execution.
    This is the granular, step-by-step control point.
    """

    priority: ClassVar[int] = 100

    @abstractmethod
    async def intercept(
        self,
        context: "RunContext",
        step: "WorkflowStep",
        next_handler: Callable[[], Awaitable[Any]],
    ) -> Any:
        """
        Intercepts a workflow step execution. Must call `await next_handler()`
        to proceed down the chain.
        """
        raise NotImplementedError
