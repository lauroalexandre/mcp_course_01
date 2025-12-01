from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool(
    name="read_document",
    description="Reads the contents of a document given its string ID.",
)
def read_document(
    doc_id: str = Field(description="The ID of the document to read."),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found.")
    return docs[doc_id]

@mcp.tool(
    name="edit_document",
    description="Edits the contents of a document given its string ID and new content.",
)
def edit_document(
    doc_id: str = Field(description="The ID of the document to edit."),
    old_str: str = Field(description="The old content to be replaced in the document."),
    new_str: str = Field(description="The new content to replace the old content with."),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found.")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)


# Resources
@mcp.resource("docs://documents")
def list_document_ids() -> str:
    """Returns a list of all available document IDs"""
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}")
def get_document_content(doc_id: str) -> str:
    """Returns the content of a specific document"""
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found.")
    return docs[doc_id]


# Prompts
@mcp.prompt(
    name="rewrite_markdown",
    description="Rewrites a document in markdown format",
)
def rewrite_in_markdown(doc_id: str = Field(description="The ID of the document to rewrite")) -> list:
    """Prompt to rewrite a document in markdown format"""
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found.")

    return [
        {
            "role": "user",
            "content": f"Please rewrite the following document in proper markdown format:\n\n{docs[doc_id]}"
        }
    ]


@mcp.prompt(
    name="summarize",
    description="Summarizes a document",
)
def summarize_document(doc_id: str = Field(description="The ID of the document to summarize")) -> list:
    """Prompt to summarize a document"""
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found.")

    return [
        {
            "role": "user",
            "content": f"Please provide a concise summary of the following document:\n\n{docs[doc_id]}"
        }
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
