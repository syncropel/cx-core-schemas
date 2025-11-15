# cx-kit/src/cx_kit/contracts/capability.py

"""
Defines the core, abstract contracts for all pluggable capabilities in the
Syncropel ecosystem. Every strategy, session manager, or remote executor
plugin must implement one of these base classes.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, ClassVar, Dict, List, TYPE_CHECKING
from contextlib import asynccontextmanager
from pydantic import BaseModel

if TYPE_CHECKING:
    from ..schemas.context import RunContext
    from ..schemas.workflow import WorkflowStep
    from ..schemas.results import StepResult
    from ..schemas.agent import FunctionSignature
    from ..schemas.jobs import JobPayload, JobHandle, JobStatus


class BaseCapability(ABC):
    """
    The unified, abstract contract for ANY pluggable capability in the Syncropel ecosystem.

    A Capability is a self-contained, discoverable class that advertises its functions
    and knows how to execute them. This is the single contract for all standard,
    stateless plugins.
    """

    capability_id: ClassVar[str]

    def __init__(self, services: Dict[str, Any]):
        """
        The constructor for dependency injection. The orchestrator will pass a
        dictionary of available SDK services.
        """
        pass

    @abstractmethod
    def get_functions(self) -> List["FunctionSignature"]:
        """
        Advertises the functions this capability provides to the system.
        """
        raise NotImplementedError

    @abstractmethod
    async def execute_function(
        self, function_name: str, context: "RunContext", parameters: BaseModel
    ) -> "StepResult":
        """
        The single entry point to execute a specific, validated function of this capability.
        """
        raise NotImplementedError

    async def shutdown(self):
        """
        A lifecycle hook called by the engine during a graceful shutdown.
        Capabilities should use this to close network connections,
        clean up temporary files, or release other resources.
        """
        # The default implementation does nothing.
        pass


class BaseStatefulSessionCapability(BaseCapability):
    """
    An abstract contract for capabilities that manage a long-lived, stateful session,
    like a browser or a persistent database connection pool.
    """

    @abstractmethod
    @asynccontextmanager
    async def session_context(
        self, context: "RunContext", step: "WorkflowStep"
    ) -> AsyncIterator[Any]:
        """
        Yields a stateful session client. The WorkflowEngine will manage this
        context across multiple steps in a flow.
        """
        yield


class BaseRemoteExecutorCapability(BaseCapability):
    """
    An abstract contract for capabilities that dispatch computation to a remote,
    asynchronous backend (like Knative or Kubernetes Jobs).
    """

    @abstractmethod
    async def dispatch(self, context: "RunContext", job: "JobPayload") -> "JobHandle":
        """
        Submits a job for remote execution and returns immediately with a handle.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_status(self, job_handle: "JobHandle") -> "JobStatus":
        """Checks the status of a dispatched job using its handle."""
        raise NotImplementedError

    @abstractmethod
    async def get_result(self, job_handle: "JobHandle") -> "StepResult":
        """Blocks and retrieves the final result of a completed job."""
        raise NotImplementedError

    @abstractmethod
    async def terminate(self, job_handle: "JobHandle") -> None:
        """Terminates or cancels a running remote job."""
        raise NotImplementedError
