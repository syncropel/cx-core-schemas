# cx-kit/src/cx_kit/utils/templating.py

"""
Provides low-level, pure-Python utilities for Jinja2 templating.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from jinja2 import Environment, TemplateError


def sql_quote_filter(value: Any) -> str:
    """A Jinja2 filter to safely quote values for inclusion in SQL strings."""
    if value is None:
        return "NULL"
    # Basic protection against SQL injection by escaping single quotes.
    return f"'{str(value).replace("'", "''")}'"


def create_jinja_environment() -> Environment:
    """
    Creates and configures a standard Jinja2 environment with custom filters
    and globals for use by the WorkflowEngine and other components.
    """
    # autoescape=False is generally safer for a system that generates code
    # and structured data, as we want to control escaping explicitly.
    jinja_env = Environment(autoescape=False)

    # Register custom filters
    jinja_env.filters["sqlquote"] = sql_quote_filter

    # Register custom global functions
    def get_now(tz: str | None = None) -> datetime:
        """A global function for templates to get the current time."""
        if tz and tz.lower() == "utc":
            return datetime.now(timezone.utc)
        return datetime.now()

    jinja_env.globals["now"] = get_now
    return jinja_env


def recursive_render(data: Any, context: Dict, jinja_env: Environment) -> Any:
    """
    Recursively traverses a data structure (dicts, lists) and renders any
    string values that contain Jinja2 template expressions.

    A special heuristic is used to evaluate strings that are *only* a Jinja
    expression (e.g., "{{ my_list }}") to their native Python type, rather
    than casting them to a string. This allows for dynamic data structures.

    Args:
        data: The data structure to render (e.g., a parsed YAML block).
        context: The dictionary of values available to the templates.
        jinja_env: The configured Jinja2 Environment instance to use.

    Returns:
        A new data structure with all template expressions rendered.
    """
    if isinstance(data, dict):
        return {k: recursive_render(v, context, jinja_env) for k, v in data.items()}
    if isinstance(data, list):
        return [recursive_render(i, context, jinja_env) for i in data]

    if isinstance(data, str):
        stripped_data = data.strip()

        # Heuristic: If the string is ONLY a Jinja expression block, evaluate it
        # directly to preserve its native Python type (e.g., a list, int, dict).
        if (
            stripped_data.startswith("{{")
            and stripped_data.endswith("}}")
            and stripped_data.count("{{") == 1
        ):
            expression = stripped_data[2:-2].strip()
            try:
                # Use compile_expression for direct evaluation to a Python object.
                return jinja_env.compile_expression(expression)(**context)
            except Exception:
                # Fallback to standard string rendering on any evaluation error.
                pass

        # For standard interpolation (e.g., "Hello {{ name }}") or fallbacks,
        # render as a string.
        if "{{" in data:
            try:
                template = jinja_env.from_string(data)
                return template.render(context)
            except TemplateError as e:
                raise ValueError(
                    f"Jinja rendering failed for template '{data}': {e}"
                ) from e

    # For all other types (int, bool, etc.), return the value as is.
    return data
