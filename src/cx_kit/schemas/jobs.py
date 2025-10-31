# cx-kit/src/cx_kit/schemas/jobs.py

"""
Defines the data contracts for asynchronous, distributed computation.

These schemas are used by `BaseRemoteExecutorStrategy` implementations to
package, dispatch, and monitor jobs on remote compute infrastructure
like Kubernetes or Knative.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional


class JobPayload(BaseModel):
    """
    The complete "job ticket" sent to a remote executor. It contains
    everything a remote worker needs to perform a computation.
    """

    run_id: str = Field(
        ..., description="The ID of the parent workflow run for correlation."
    )
    step_id: str = Field(..., description="The ID of the specific step being executed.")

    # Specifies the execution environment for the remote worker.
    # This could be a Docker image, a Nix flake URI, etc.
    environment_id: str = Field(
        ...,
        description="Identifier for the remote execution environment (e.g., a Docker image).",
    )

    code: Optional[str] = Field(
        None, description="The code to be executed by the worker."
    )
    language: Optional[str] = Field(
        None, description="The language of the code (e.g., 'python', 'r')."
    )
    input_data: Any = Field(None, description="The piped-in data for the job.")

    callback_url: str = Field(
        ..., description="The secure URL the worker must call to report its result."
    )

    # An open dictionary for executor-specific parameters.
    executor_params: Dict[str, Any] = Field(default_factory=dict)


class JobHandle(BaseModel):
    """
    A handle or "tracking number" returned immediately after a job is dispatched.
    It contains the necessary information for the orchestrator to check the job's status later.
    """

    job_id: str = Field(
        ...,
        description="The unique identifier for the job in the remote compute system (e.g., a Kubernetes Job name).",
    )
    provider: str = Field(
        ..., description="The key of the executor provider that created this job."
    )

    # An open dictionary for provider-specific tracking information.
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JobStatus(BaseModel):
    """A standardized schema for the status of a remote job."""

    status: Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "UNKNOWN"]
    message: Optional[str] = Field(None, description="A human-readable status message.")
    start_time: Optional[str] = None
    completion_time: Optional[str] = None
