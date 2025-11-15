# cx-kit/src/cx_kit/contracts/workflow.py

"""
Defines the contracts for the Interception & Extension Protocol (IEP).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Awaitable, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..schemas.context import RunContext
    from ..schemas.document import CodeBlock
    from ..schemas.results import BlockResult


class BaseBlockInterceptor(ABC):
    """
    The contract for a plugin that intercepts a SINGLE code block's execution.
    This is the primary extension point for cross-cutting concerns like caching
    and logging in the native CXQL runtime.
    """

    priority: int = 100

    @abstractmethod
    async def intercept(
        self,
        context: "RunContext",
        block: "CodeBlock",
        next_handler: Callable[[RunContext], Awaitable["BlockResult"]],
    ) -> "BlockResult":
        """
        Intercepts a code block execution. Must call `await next_handler(context)`
        to proceed down the chain.

        Args:
            context: The current, immutable RunContext for the execution.
            block: The CodeBlock object being executed. Contains id, attributes, and content.
            next_handler: An awaitable callable representing the rest of the execution
                          pipeline. It MUST be called with the context.

        Returns:
            A BlockResult object, either from a cache or from the next_handler.
        """
        raise NotImplementedError
