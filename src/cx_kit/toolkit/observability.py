# cx-kit/src/cx_kit/toolkit/observability.py

"""
Provides the observability toolkit for the cx-kit SDK.

This module contains the `get_logger` helper, which is the mandatory entry
point for obtaining a context-aware, structured logger anywhere in the system.
"""

import structlog
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..schemas.context import RunContext


def get_logger(context: "RunContext", block_id: Optional[str] = None, **kwargs):
    """
    Returns a structlog logger pre-bound with critical trace information.

    This is the canonical way for any component in the system to obtain a logger.
    It automatically binds the `run_id` from the context. The `block_id` is an
    explicit optional argument, allowing components to add block-level context
    only when it's available and relevant.

    Args:
        context: The current `RunContext` for the execution.
        block_id: (Optional) The ID of the code block being executed.
        **kwargs: Additional key-value pairs to bind to the logger.

    Returns:
        A pre-bound structlog logger instance.
    """
    if not hasattr(context, "run_id"):
        # This is a safeguard against malformed or incomplete context objects.
        return structlog.get_logger().bind(**kwargs)

    bindings = {"run_id": context.run_id}

    # The block_id is now an explicit parameter, not an assumed attribute of the context.
    # This decouples the logger from the specific shape of the RunContext model.
    if block_id:
        bindings["block_id"] = block_id

    return structlog.get_logger().bind(**bindings, **kwargs)
