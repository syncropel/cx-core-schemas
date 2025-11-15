# cx-kit/src/cx_kit/toolkit/observability.py

import structlog
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..schemas.context import RunContext


def get_logger(context: Optional["RunContext"] = None, **kwargs):
    """
    Returns a structlog logger pre-bound with critical trace information if available.

    This is the canonical way for any component to obtain a logger. It is now safe
    to call even without a RunContext (e.g., during startup or discovery), in
    which case it returns a logger bound only with the provided kwargs.
    """
    # Start with a base logger instance
    log = structlog.get_logger()

    # Bind context-specific fields ONLY if a valid context is provided.
    if context and hasattr(context, "run_id"):
        bindings = {"run_id": context.run_id}

        # You can add more context bindings here if needed in the future
        # e.g., if hasattr(context, "current_block") and context.current_block:
        #    bindings["block_id"] = context.current_block.id

        log = log.bind(**bindings)

    # Always bind any additional kwargs provided by the caller.
    if kwargs:
        log = log.bind(**kwargs)

    return log
