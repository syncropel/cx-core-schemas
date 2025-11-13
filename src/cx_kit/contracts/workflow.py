# cx-kit/src/cx_kit/contracts/workflow.py

"""
Defines the contracts for the Interception & Extension Protocol (IEP).

These abstract base classes allow developers to build plugins that hook into
the execution lifecycle of the native CXQL runtime.
"""

from abc import ABC, abstractmethod
from typing import Awaitable, Callable, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from ..schemas.context import RunContext
    from ..schemas.document import CodeBlock
    from ..schemas.results import BlockResult


class BaseBlockInterceptor(ABC):  # <-- RENAMED for clarity
    """
    The contract for a plugin that intercepts a SINGLE code block's execution
    in the native CXQL runtime.
    """

    priority: ClassVar[int] = 100

    @abstractmethod
    async def intercept(
        self,
        context: "RunContext",
        block: "CodeBlock",  # <-- Pass the CodeBlock model
        script_text: str,  # <-- Pass the raw script text
        is_preamble: bool,  # <-- Pass execution context
        next_handler: Callable[
            [], Awaitable["BlockResult"]
        ],  # <-- next() returns a BlockResult
    ) -> "BlockResult":
        """
        Intercepts a code block execution. Must call `await next_handler()`
        to proceed down the chain.
        """
        raise NotImplementedError
