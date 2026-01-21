#!/usr/bin/env python3
"""
Context packing utilities for the context-aware-workflow plugin.

Provides functions to extract interface signatures from TypeScript and Python
files for compact context representation.
"""

import re
import sys

# Windows UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
from typing import Any, Dict, List


def extract_typescript_interfaces(content: str) -> List[str]:
    """
    Extract interface-like signatures from TypeScript/JavaScript content.

    Extracts:
    - Function declarations (including async and exported)
    - Arrow functions (exported const)
    - Class declarations (with extends/implements)
    - Interface declarations (with extends)
    - Type declarations

    Returns list of signature strings.
    """
    interfaces = []

    # Function declarations: [export] [async] function name(params): return
    func_pattern = re.compile(
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?",
        re.MULTILINE
    )
    for match in func_pattern.finditer(content):
        sig = match.group(0).strip()
        sig = re.sub(r"\s+", " ", sig)  # Normalize whitespace
        interfaces.append(sig)

    # Arrow functions: export const name = (params): return =>
    arrow_pattern = re.compile(
        r"export\s+const\s+(\w+)\s*=\s*\([^)]*\)\s*(?::\s*[^=]+)?(?=\s*=>)",
        re.MULTILINE
    )
    for match in arrow_pattern.finditer(content):
        sig = match.group(0).strip()
        sig = re.sub(r"\s+", " ", sig)
        interfaces.append(sig)

    # Class declarations: [export] class Name [extends X] [implements Y]
    class_pattern = re.compile(
        r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?",
        re.MULTILINE
    )
    for match in class_pattern.finditer(content):
        sig = match.group(0).strip()
        sig = re.sub(r"\s+", " ", sig)
        interfaces.append(sig)

    # Interface declarations: [export] interface Name [extends X, Y]
    interface_pattern = re.compile(
        r"(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+[\w,\s]+)?",
        re.MULTILINE
    )
    for match in interface_pattern.finditer(content):
        sig = match.group(0).strip()
        sig = re.sub(r"\s+", " ", sig)
        interfaces.append(sig)

    # Type declarations: [export] type Name = ...
    type_pattern = re.compile(
        r"(?:export\s+)?type\s+(\w+)\s*=\s*([^;]+)",
        re.MULTILINE
    )
    for match in type_pattern.finditer(content):
        name = match.group(1)
        value = match.group(2).strip()
        # Truncate long type definitions
        if len(value) > 60:
            value = value[:57] + "..."
        sig = f"type {name} = {value}"
        interfaces.append(sig)

    return interfaces


def extract_python_interfaces(content: str) -> List[str]:
    """
    Extract interface-like signatures from Python content.

    Extracts:
    - Function definitions (with type hints)
    - Class definitions (with base classes)
    - Method definitions (including async)

    Returns list of signature strings.
    """
    interfaces = []

    # Function/method definitions: [async] def name(params) [-> return]:
    func_pattern = re.compile(
        r"(?:async\s+)?def\s+(\w+)\s*\([^)]*\)(?:\s*->\s*[^:]+)?:",
        re.MULTILINE
    )
    for match in func_pattern.finditer(content):
        sig = match.group(0).rstrip(":")
        sig = re.sub(r"\s+", " ", sig)  # Normalize whitespace
        interfaces.append(sig)

    # Class definitions: class Name(BaseClass, Mixin):
    class_pattern = re.compile(
        r"class\s+(\w+)(?:\s*\([^)]+\))?:",
        re.MULTILINE
    )
    for match in class_pattern.finditer(content):
        sig = match.group(0).rstrip(":")
        sig = re.sub(r"\s+", " ", sig)
        interfaces.append(sig)

    return interfaces


def format_markdown(results: List[Dict[str, Any]]) -> str:
    """
    Format extraction results as Markdown.

    Args:
        results: List of dicts with keys:
            - path: file path
            - interfaces: list of extracted signatures
            - line_count: number of lines in file
            - error: optional error message

    Returns formatted Markdown string.
    """
    output_lines = ["# Context Pack\n"]

    for result in results:
        path = result.get("path", "unknown")
        output_lines.append(f"## `{path}`\n")

        if "error" in result and result["error"]:
            output_lines.append(f"**Error**: {result['error']}\n")
            continue

        line_count = result.get("line_count", 0)
        output_lines.append(f"*{line_count} lines*\n")

        interfaces = result.get("interfaces", [])
        if not interfaces:
            output_lines.append("*No extractable interfaces*\n")
        else:
            output_lines.append("```")
            for interface in interfaces:
                output_lines.append(interface)
            output_lines.append("```\n")

    return "\n".join(output_lines)


if __name__ == "__main__":
    # Example usage
    ts_sample = """
export async function fetchUser(id: string): Promise<User> {
    return await db.findUser(id);
}

export const processData = (data: Data[]): Result => data.map(transform);

interface User {
    id: string;
    name: string;
}

class UserService implements IUserService {
    constructor() {}
}

type Status = 'active' | 'inactive' | 'pending';
"""

    py_sample = """
def process_data(data: list[dict]) -> dict:
    return {"result": data}

class DataProcessor(BaseProcessor, LogMixin):
    def __init__(self, config: Config):
        self.config = config

async def fetch_remote(url: str) -> bytes:
    pass
"""

    print("=== TypeScript Interfaces ===")
    for sig in extract_typescript_interfaces(ts_sample):
        print(f"  {sig}")

    print("\n=== Python Interfaces ===")
    for sig in extract_python_interfaces(py_sample):
        print(f"  {sig}")

    print("\n=== Formatted Output ===")
    results = [
        {"path": "src/service.ts", "interfaces": ["class Service", "function init()"], "line_count": 100},
        {"path": "missing.ts", "error": "File not found", "interfaces": []},
    ]
    print(format_markdown(results))
