# cx-kit/src/cx_kit/contracts/config.py

"""
Defines the base contract for pluggable configuration schemas.

This module provides the `BaseConfig` class, which all configuration
models for capabilities, services, or agents must inherit from.
This inheritance acts as a marker that allows the central ConfigManager
to discover these schemas via the 'syncropel.configs' entry point.
"""

from pydantic import BaseModel


class BaseConfig(BaseModel):
    """
    The abstract base class for all pluggable configuration schemas.

    Any Pydantic model that inherits from this class can be registered
    via a 'syncropel.configs' entry point. The ConfigManager will
    discover it and use it to validate the corresponding section
    in the user's `config.yaml` files.

    Example:
        A `cx-capability-dbt` plugin would define:

        ```python
        class DbtCapabilityConfig(BaseConfig):
            project_dir: str = '~/dbt_projects/default'
            profiles_dir: str = '~/.dbt/'
        ```

        And register it in its `pyproject.toml`:

        ```toml
        [project.entry-points."syncropel.configs"]
        "dbt" = "cx_dbt.config:DbtCapabilityConfig"
        ```
    """

    pass
