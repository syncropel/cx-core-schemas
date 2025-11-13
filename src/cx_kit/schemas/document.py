# cx-kit/src/cx_kit/schemas/document.py

"""
Defines the schemas for the structural representation of a literate (.cxql.md) document.

These models are produced by a high-level Markdown parser and represent the
document's composition of narrative and code, but not the computational meaning
of the code itself.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

# A type hint for the union of possible block types.
DocumentBlock = Union["MarkdownBlock", "CodeBlock"]


class MarkdownBlock(BaseModel):
    """Represents a block of narrative Markdown content."""

    type: Literal["markdown"] = "markdown"
    content: str = Field(..., description="The raw Markdown content of the block.")


class CodeBlock(BaseModel):
    """
    Represents a fenced code block containing executable CXQL code.
    """

    type: Literal["code"] = "code"
    id: Optional[str] = Field(
        None, description="The unique identifier for the block, e.g., 'preamble'."
    )
    content: str = Field(..., description="The raw CXQL source code within the block.")
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary of attributes parsed from the block's info string, e.g., {'hidden': True}.",
    )
    start_line: int = Field(
        ...,
        description="The 1-based line number where this block starts in the source file.",
    )


class ParsedDocument(BaseModel):
    """
    Represents the complete structural breakdown of a .cxql.md file.
    This is the primary input for the DocumentOrchestrator.
    """

    frontmatter: Dict[str, Any] = Field(
        default_factory=dict, description="YAML frontmatter from the top of the file."
    )
    blocks: List[DocumentBlock] = Field(
        default_factory=list,
        description="A sequential list of all markdown and code blocks.",
    )


# This is a forward reference update required by Pydantic v2.
# It helps the type hint `DocumentBlock` resolve the class names.
MarkdownBlock.model_rebuild()
CodeBlock.model_rebuild()
