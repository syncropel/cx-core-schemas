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
    from ..schemas.project import Block


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


def calculate_cache_key(
    rendered_block: "Block", capability_version: str, parent_hashes: Dict[str, str]
) -> str:
    """
    Calculates a deterministic, content-addressable cache key (SHA256) for a
    block based on its fully rendered semantic content, the version of the
    capability that will execute it, and the content hashes of its parents.
    """
    hasher = hashlib.sha256()

    # 1. Define the complete set of fields that constitute the semantic identity.
    semantic_fields = {
        "engine",
        "connection",
        "run",
        "content",
        "inputs",
        "outputs",
        "if_condition",
    }

    # 2. Create a dictionary with only these fields from the *rendered* block.
    block_dict = rendered_block.model_dump(by_alias=True)
    semantic_dict = {
        k: block_dict.get(k) for k in semantic_fields if block_dict.get(k) is not None
    }

    # 3. Serialize and hash this semantic dictionary.
    semantic_str = json.dumps(semantic_dict, sort_keys=True)
    hasher.update(semantic_str.encode("utf-8"))

    # 4. CRITICAL: Include the capability's version in the hash.
    hasher.update(capability_version.encode("utf-8"))

    # 5. Include parent hashes to ensure full data lineage affects the key.
    for block_id, hash_val in sorted(parent_hashes.items()):
        hasher.update(f"{block_id}:{hash_val or ''}".encode("utf-8"))

    return f"sha256:{hasher.hexdigest()}"
