from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


# --- Base Action Model ---
# All specific actions will inherit from this to ensure the 'action'
# field is present for Pydantic's discriminated union.
class BaseAction(BaseModel):
    action: str


# --- Standard Stateless Action Models ---


class RunSqlQueryAction(BaseAction):
    action: Literal["run_sql_query"]
    query: str = Field(
        ..., description="The SQL query string or a 'file:/path/to/query.sql' URI."
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters to pass to the query."
    )


class RunMultiQueryAction(BaseAction):
    action: Literal["run_multi_query"]
    targets: List[str] = Field(
        ..., description="The list of collections/targets to query."
    )
    filter: str = Field(..., description="The filter string to apply to each target.")
    blueprint_action: str = Field(
        default="query",
        description="The name of the action in the blueprint to call for each target.",
    )


class RunFlowAction(BaseAction):
    action: Literal["run_flow"]
    flow_name: str = Field(..., description="The name of the flow to execute.")
    inputs: Dict[str, Any] = Field(
        default_factory=dict, description="Input parameters for the sub-flow."
    )


class TestConnectionAction(BaseAction):
    action: Literal["test_connection"]


class BrowsePathAction(BaseAction):
    action: Literal["browse_path"]
    path: str = Field(default="/", description="The virtual path to browse.")


class ReadContentAction(BaseAction):
    action: Literal["read_content"]
    path: str = Field(..., description="The virtual path of the file to read.")


class RunDeclarativeAction(BaseAction):
    action: Literal["run_declarative_action"]
    template_key: str = Field(
        ..., description="The key of the action template to use from the ApiCatalog."
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Data to be passed into the action's Jinja2 template.",
    )


class AggregateContentAction(BaseAction):
    action: Literal["aggregate_content"]
    source_paths: Optional[List[str]] = Field(
        None, description="A static list of local file or directory paths to aggregate."
    )
    source_results: Optional[List[str]] = Field(
        None,
        description="A list of result objects from previous 'browse' steps, referenced via Jinja.",
    )
    target_path: str = Field(
        ..., description="The VFS path for the aggregated output file."
    )
    header_template: Optional[str] = Field(
        None, description="A Jinja2 template for the file header."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata for rendering the header."
    )

    @model_validator(mode="after")
    def check_at_least_one_source(self) -> "AggregateContentAction":
        if not self.source_paths and not self.source_results:
            raise ValueError(
                "At least one of 'source_paths' or 'source_results' must be provided."
            )
        return self


class RunPythonScriptAction(BaseAction):
    action: Literal["run_python_script"]
    script_path: str = Field(
        ..., description="The path to the Python script to execute."
    )
    input_data_json: str = Field(
        "{}", description="A JSON string to be passed to the script's stdin."
    )
    args: List[str] = Field(default_factory=list)  # <-- ADD THIS


class FileToWrite(BaseModel):
    path: str = Field(
        ..., description="The destination path for the file, can be a Jinja template."
    )
    content: str = Field(
        ..., description="The content of the file, can be a Jinja template."
    )


class WriteFilesAction(BaseAction):
    action: Literal["write_files"]
    files: List[FileToWrite] = Field(
        ..., description="A list of file objects, each with a path and content."
    )


class RunTransformAction(BaseAction):
    action: Literal["run_transform"]
    script_path: str = Field(
        ..., description="The path to the .transformer.yaml script to execute."
    )
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary containing data to be passed to the transformer's context.",
    )


# --- Stateful Browser Action Models ---


class BrowserNavigateAction(BaseAction):
    """Navigates the browser to a specific URL."""

    action: Literal["browser_navigate"]
    url: str = Field(..., description="The URL to navigate the browser to.")


class BrowserClickAction(BaseAction):
    """Clicks an element on the page."""

    action: Literal["browser_click"]
    target: str = Field(
        ..., description="The CSS selector or locator for the element to click."
    )
    timeout: Optional[int] = Field(
        None, description="Optional timeout in milliseconds."
    )


class BrowserTypeAction(BaseAction):
    """Types text into an input element."""

    action: Literal["browser_type"]
    target: str = Field(..., description="The CSS selector for the input element.")
    text: str = Field(..., description="The text to type into the element.")
    timeout: Optional[int] = Field(
        None, description="Optional timeout in milliseconds."
    )


class BrowserGetHtmlAction(BaseAction):
    """Retrieves the full HTML content of the current page."""

    action: Literal["browser_get_html"]


class BrowserGetLocalStorageAction(BaseAction):
    """Retrieves all data from the browser's local storage."""

    action: Literal["browser_get_local_storage"]


class AssetReadBlockAction(BaseAction):
    action: Literal["asset.read_block"]
    notebook_id: str
    block_id: str
    mode: Literal["raw_text", "parse_yaml", "parse_json"] = "raw_text"


class AssetPatchBlockAction(BaseAction):
    action: Literal["asset.patch_block"]
    notebook_id: str
    block_id: str
    target_path: str
    source_data: Any
    source_path_key: str
    value_map: Dict[str, str]


class PublishAction(BaseAction):
    action: Literal["publish"]
    source: Literal["data", "notebook"] = Field(
        "data",
        description="Specifies what is being published: 'data' from a pipeline or a full 'notebook'.",
    )
    name: Optional[str] = Field(
        None,
        description="The logical ID of the notebook to publish. Required when source is 'notebook'.",
    )
    input_data: Optional[Any] = Field(
        None,
        description="The data to be rendered, typically from a previous step. Used when source is 'data'.",
    )

    to: Optional[str] = Field(
        None,
        description="The target format (e.g., 'html', 'excel'). If omitted, it will be inferred from the output file extension.",
    )
    output: Optional[str] = Field(
        None,
        description="The output file path. If omitted for a notebook, a default will be generated.",
    )

    params: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters to pass to the renderer."
    )


# --- Discriminated Union of ALL Possible Actions ---
# Pydantic uses this to determine which model to validate based on the 'action' field.
AnyConnectorAction = Union[
    # Standard Stateless Actions
    TestConnectionAction,
    BrowsePathAction,
    ReadContentAction,
    RunSqlQueryAction,
    RunDeclarativeAction,
    AggregateContentAction,
    RunPythonScriptAction,
    WriteFilesAction,
    RunTransformAction,
    # Stateful Browser Actions
    BrowserNavigateAction,
    BrowserClickAction,
    BrowserTypeAction,
    BrowserGetHtmlAction,
    BrowserGetLocalStorageAction,
    # multi steps flows and actions
    RunMultiQueryAction,
    RunFlowAction,
    AssetReadBlockAction,
    AssetPatchBlockAction,
    PublishAction,
]


# --- Core Scripting Models ---


class ConnectorStep(BaseModel):
    """
    Defines a single, executable or static step/block within a declarative workflow.
    This model is now flexible enough to represent both flow steps and notebook blocks.
    """

    id: str

    # 'name' is now optional, as Markdown blocks won't have it.
    name: Optional[str] = None

    description: str | None = None

    engine: Optional[
        Literal[
            "markdown",
            "sql",
            "python",
            "transform",
            "ui-component",
            "stream",
            "agent",
            "cx-action",
            "shell",
            "run",
            "yaml",
            "publish",
            "artifact",
        ]
    ] = Field(
        None, description="The execution engine for this step (e.g., 'sql', 'python')."
    )
    run: Optional[AnyConnectorAction] = Field(
        None,
        discriminator="action",
        description="The declarative action payload for this step.",
    )
    # NEW: The 'content' field for notebook blocks.
    content: Optional[str] = Field(
        None, description="The source code or text content for notebook blocks."
    )

    connection_source: Optional[str] = Field(
        default=None, description="Source identifier, e.g., 'user:my_db'"
    )

    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="A dictionary of step-local variables for Jinja rendering.",
    )

    # 'inputs' is now a simple list of strings, matching the Block model.
    inputs: List[str] = Field(
        default_factory=list,
        description="A list of dependencies on outputs from other steps, specified as 'step_id.output_name'.",
    )

    # 'outputs' can now be a list (notebooks) or a dict (flows).
    outputs: Union[List[str], Dict[str, str], None] = Field(
        None,
        description="A list of output names (for notebooks) or a dict of name:jmespath pairs (for flows).",
    )

    depends_on: Optional[List[str]] = Field(
        None,
        description="A list of step IDs that must complete before this step can run.",
    )
    if_condition: Optional[str] = Field(
        None,
        alias="if",
        description="A Jinja2 expression that must evaluate to true for the step to run.",
    )
    cache_config: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class ScriptInputParameter(BaseModel):
    """Defines a single expected input parameter for a script."""

    description: str
    type: str = "string"  # Default type
    required: bool = False
    default: Optional[Any] = None


class ConnectorScript(BaseModel):
    """The root model for a declarative .flow.yaml file."""

    name: str
    description: str | None = None
    # THIS IS THE NEW, CRITICAL FIELD FOR STATEFUL PROVIDERS
    session_provider: Optional[str] = Field(
        None, description="The key for a stateful session provider, e.g., 'browser'."
    )
    inputs: Optional[Dict[str, ScriptInputParameter]] = Field(
        None, description="A schema defining the expected parameters for this script."
    )
    steps: List[ConnectorStep]
    cache_config: Optional[Dict[str, Any]] = None
    script_input: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Placeholder for data piped from stdin."
    )
    runtime_input: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Placeholder for data piped from stdin.",
        exclude=True,
    )
