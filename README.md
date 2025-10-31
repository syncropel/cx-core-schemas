# Syncropel `cx-kit`

### The Official SDK for the Syncropel Capability Fabric

[![PyPI version](https://badge.fury.io/py/cx-kit.svg)](https://badge.fury.io/py/cx-kit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Welcome to `cx-kit`, the foundational Software Development Kit for building on the Syncropel platform. This lightweight library provides all the core contracts, data schemas, and developer tools necessary to create first-class, pluggable **Capabilities** for the `cx-shell` orchestrator.

If you want to teach Syncropel how to connect to a new API, run a new type of analysis, or interact with a new tool, this is where you start.

---

## Core Philosophy: The Capability Fabric

The Syncropel platform is a lean orchestrator (`cx-shell`) that knows how to run computational workflows but knows nothing about specific tools. All functionality—from connecting to databases to running AI agents—is provided by independent, discoverable plugins called **Capabilities**.

The `cx-kit` provides the language and tools to build these capabilities. It is designed around three core principles:

1.  **Declarative Contracts:** Define _what_ your capability does using clean, abstract base classes.
2.  **Schema-Driven:** Use powerful Pydantic models for all data, ensuring type safety and clarity.
3.  **Developer Ergonomics:** Leverage a rich toolkit of helpers for common tasks like logging, secrets management, and AI interaction.

## Quick Start: Building Your First Capability

Let's build a simple "Hello World" capability in 5 minutes. This capability will take a `name` as input and return a greeting.

### 1. Project Setup

First, set up your project directory and install `cx-kit`.

```bash
# Create your project
mkdir cx-capability-hello
cd cx-capability-hello
mkdir -p src/cx_hello

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the Syncropel SDK
pip install cx-kit
```

### 2. Define the Capability (`strategy.py`)

Create a file `src/cx_hello/strategy.py`. This is where you'll implement the core logic.

```python
# src/cx_hello/strategy.py

from pydantic import BaseModel, Field
from typing import List

# Import the core contracts and schemas from the SDK
from cx_kit.contracts.capability import BaseCapability
from cx_kit.schemas.context import RunContext
from cx_kit.schemas.workflow import WorkflowStep
from cx_kit.schemas.results import StepResult
from cx_kit.schemas.agent import FunctionSignature

# Define the Pydantic model for our function's parameters
class GreetParameters(BaseModel):
    name: str = Field("World", description="The name to include in the greeting.")

class HelloCapability(BaseCapability):
    """A simple example capability that provides a greeting function."""

    # 1. Register the unique ID for this capability.
    capability_id = "community:hello"

    def __init__(self, services):
        """The orchestrator injects services here. We don't need any for this simple example."""
        super().__init__(services)

    # 2. Advertise the functions this capability provides.
    def get_functions(self) -> List[FunctionSignature]:
        return [
            FunctionSignature(
                name="greet",
                description="Generates a friendly greeting.",
                parameters=GreetParameters
            )
        ]

    # 3. Implement the execution logic for the advertised functions.
    async def execute_function(self, function_name: str, context: RunContext, parameters: BaseModel) -> StepResult:
        if function_name == "greet":
            # Safely cast the generic parameters to our specific Pydantic model
            if isinstance(parameters, GreetParameters):
                greeting = f"Hello, {parameters.name}!"

                # All capabilities must return a structured StepResult.
                return StepResult(data=greeting)

        raise NotImplementedError(f"Function '{function_name}' is not implemented by this capability.")

```

### 3. Make It Pluggable (`pyproject.toml`)

Create a `pyproject.toml` in your project root to define the package and register it as a Syncropel plugin.

```toml
# pyproject.toml

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "cx-capability-hello"
version = "0.1.0"
description = "A simple example capability for the Syncropel platform."
dependencies = [
    "cx-kit>=0.3.0" # Declare dependency on the SDK
]

[tool.setuptools.packages.find]
where = ["src"]

# This is the magic that makes your capability discoverable by cx-shell
[project.entry-points."syncropel.capabilities"]
"community:hello" = "cx_hello.strategy:HelloCapability"
```

### 4. Install and Run

Install your new capability in your `cx-shell` environment.

```bash
# Install your local package in editable mode
pip install -e .
```

Now, you can use your new capability directly in a `.cx.md` notebook!

```yaml
# In a .cx.md file:
cx_block: true
id: say_hello
engine: community:hello # Use the capability_id as the engine
run:
  action: greet # Use the function_name as the action
  parameters:
    name: "Syncropel Developer"
```

When you run this block, the `WorkflowEngine` will discover your `community:hello` plugin, load it, validate the `parameters` against your `GreetParameters` model, and execute your `execute_function` method.

## The `cx-kit` Modules

The SDK is organized into logical modules to help you find what you need.

- **`cx_kit.contracts`**: The abstract base classes (`BaseCapability`, `BaseAgentSkill`, etc.) that define the core interfaces for all pluggable components.
- **`cx_kit.schemas`**: All the Pydantic data models (`WorkflowStep`, `RunContext`, `StepResult`, `FunctionSignature`) that describe the data flowing through the Syncropel fabric.
- **`cx_kit.toolkit`**: High-level helper classes and functions that provide "batteries-included" functionality for common tasks like secrets management (`ConnectionSecrets`), AI interaction (`AgenticInterface`), and observability (`get_logger`).
- **`cx_kit.utils`**: Pure, low-level, stateless utility functions for tasks like serialization and templating.

By building on these primitives, you can rapidly develop powerful, robust, and seamlessly integrated capabilities for the Syncropel ecosystem.
