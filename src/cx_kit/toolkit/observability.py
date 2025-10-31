# cx-kit/src/cx_kit/toolkit/observability.py

"""
Provides the observability toolkit for the cx-kit SDK.

This module contains helpers that enable capability developers to easily
produce structured, context-aware logs that integrate seamlessly with the
Syncropel platform's observability stack.
"""

from typing import TYPE_CHECKING
import structlog

# Use TYPE_CHECKING to avoid runtime circular dependencies while providing type hints.
if TYPE_CHECKING:
    from ..schemas.context import RunContext
    from ..schemas.workflow import WorkflowStep


def get_logger(context: "RunContext", step: "WorkflowStep", **kwargs):
    """
    Returns a pre-configured `structlog` logger that is automatically bound
    with essential trace information from the current execution context.

    By using this helper, logs generated from any capability will be
    automatically correlated with the specific run, flow, and step that
    produced them, enabling powerful, targeted debugging and analysis.

    Args:
        context: The `RunContext` for the current step execution.
        step: The `WorkflowStep` object being executed.
        **kwargs: Additional key-value pairs to bind to the logger context.

    Returns:
        A bound structlog logger instance.

    Example:
        ```python
        # Inside a Capability's execute_function method:
        from cx_kit.toolkit.observability import get_logger

        async def execute_function(self, function_name, context, parameters):
            log = get_logger(context, step, capability_id=self.capability_id)

            log.info("Starting API call.", target_url=url)
            # ... do work ...
            log.info("API call successful.", record_count=100)
        ```
    """
    # Get the base logger for the application.
    base_logger = structlog.get_logger()

    # Bind the essential context for tracing and observability.
    return base_logger.bind(
        run_id=context.run_id,
        flow_id=context.flow_id,
        step_id=step.id,
        capability_id=step.engine
        or (step.run.get("action") if step.run else "unknown"),
        **kwargs,
    )
