# cx-kit/src/cx_kit/utils/orchestration.py

"""
Provides low-level, pure-Python utilities for workflow orchestration,
including dependency graph construction and caching logic.
"""

import hashlib
import json
from typing import Dict, List, TYPE_CHECKING

# Use TYPE_CHECKING to avoid a hard dependency on networkx at runtime,
# allowing it to be a dependency of the orchestrator (`cx-shell`) instead
# of the core SDK, though making it a core SDK dep is also a valid choice.
if TYPE_CHECKING:
    from ..schemas.workflow import WorkflowStep
    from networkx import DiGraph


def build_dependency_graph(steps: List["WorkflowStep"]) -> "DiGraph":
    """
    Builds a directed acyclic graph (DAG) from a list of workflow steps
    using the 'networkx' library.

    This function is the foundation of the WorkflowEngine's execution plan,
    ensuring that steps are run in the correct order based on their explicit

    `depends_on` and implicit `inputs` declarations.

    Args:
        steps: A list of `WorkflowStep` objects.

    Returns:
        A `networkx.DiGraph` object representing the workflow.

    Raises:
        ValueError: If a circular dependency is detected in the workflow.
    """
    import networkx as nx  # Lazy import for this heavy dependency

    dag = nx.DiGraph()
    step_map = {step.id: step for step in steps}

    for step in steps:
        dag.add_node(step.id, step_data=step)

        # Add explicit dependencies from the 'depends_on' field
        if step.depends_on:
            for dep_id in step.depends_on:
                if dep_id in step_map:
                    dag.add_edge(dep_id, step.id)
                else:
                    raise ValueError(
                        f"Step '{step.id}' has an invalid dependency: '{dep_id}'"
                    )

        # Add implicit dependencies from the 'inputs' field (e.g., "step_a.output")
        if step.inputs:
            for input_str in step.inputs:
                if "." in input_str:
                    dep_id = input_str.split(".", 1)[0]
                    if dep_id in step_map and dep_id != step.id:
                        dag.add_edge(dep_id, step.id)

    if not nx.is_directed_acyclic_graph(dag):
        try:
            cycle = nx.find_cycle(dag, orientation="original")
            raise ValueError(f"Workflow contains a circular dependency: {cycle}")
        except nx.NetworkXNoCycle:
            # This can happen in complex graphs; the initial check is sufficient.
            raise ValueError("Workflow contains a circular dependency.")

    return dag


def calculate_cache_key(step: "WorkflowStep", parent_hashes: Dict[str, str]) -> str:
    """
    Calculates a deterministic, content-addressable cache key (SHA256) for a
    workflow step based on its definition and the content hashes of its parents.

    This ensures that a step is only re-executed if its own definition or the
    output of any of its direct dependencies has changed, enabling perfect,
    automatic incremental computation.

    Args:
        step: The `WorkflowStep` object to be hashed.
        parent_hashes: A dictionary mapping the step IDs of all parent steps
                       to their `output_hash`.

    Returns:
        A string representing the SHA256 cache key, prefixed with "sha256:".
    """
    hasher = hashlib.sha256()

    # Use by_alias=True to get 'if' instead of 'if_condition' for determinism
    # and exclude_none=True to keep the hash stable if optional fields are absent.
    step_def_dict = step.model_dump(by_alias=True, exclude_none=True)
    step_def_str = json.dumps(step_def_dict, sort_keys=True)
    hasher.update(step_def_str.encode("utf-8"))

    # Include parent hashes in a deterministic order to ensure the full
    # lineage is part of the key.
    sorted_parent_hashes = sorted(parent_hashes.items())
    for step_id, hash_val in sorted_parent_hashes:
        hasher.update(f"{step_id}:{hash_val or ''}".encode("utf-8"))

    return f"sha256:{hasher.hexdigest()}"
