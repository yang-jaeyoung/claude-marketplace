#!/usr/bin/env python3
"""
Unit tests for pack_context.py

Tests the interface extraction functions for TypeScript and Python.
"""

import sys
import unittest
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "skills" / "context-manager" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from pack_context import (
    extract_typescript_interfaces,
    extract_python_interfaces,
    format_markdown,
)


class TestExtractTypescriptInterfaces(unittest.TestCase):
    """Test TypeScript/JavaScript interface extraction."""

    def test_function_declaration(self):
        """Extract regular function declarations."""
        content = """
        function greet(name: string): string {
            return "Hello " + name;
        }
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("function greet" in i for i in interfaces))
        self.assertTrue(any("string" in i for i in interfaces))

    def test_async_function(self):
        """Extract async function declarations."""
        content = """
        async function fetchData(url: string): Promise<Data> {
            return await fetch(url);
        }
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("function fetchData" in i for i in interfaces))

    def test_exported_function(self):
        """Extract exported functions."""
        content = """
        export function calculate(a: number, b: number): number {
            return a + b;
        }
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("function calculate" in i for i in interfaces))

    def test_arrow_function(self):
        """Extract exported arrow functions."""
        content = """
        export const add = (a: number, b: number): number => a + b;
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("const add" in i for i in interfaces))

    def test_class_declaration(self):
        """Extract class declarations."""
        content = """
        class UserService {
            constructor() {}
        }
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("class UserService" in i for i in interfaces))

    def test_class_extends(self):
        """Extract class with extends."""
        content = """
        export class AdminUser extends User {
        }
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("extends User" in i for i in interfaces))

    def test_class_implements(self):
        """Extract class with implements."""
        content = """
        class AuthService implements IAuthService {
        }
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("implements IAuthService" in i for i in interfaces))

    def test_interface_declaration(self):
        """Extract interface declarations."""
        content = """
        interface User {
            id: string;
            name: string;
        }
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("interface User" in i for i in interfaces))

    def test_interface_extends(self):
        """Extract interface with extends."""
        content = """
        export interface AdminUser extends User, Permissions {
            role: string;
        }
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("interface AdminUser" in i for i in interfaces))
        self.assertTrue(any("extends User" in i for i in interfaces))

    def test_type_declaration(self):
        """Extract type declarations."""
        content = """
        export type Status = 'pending' | 'active' | 'completed';
        """
        interfaces = extract_typescript_interfaces(content)
        self.assertTrue(any("type Status" in i for i in interfaces))

    def test_long_type_truncation(self):
        """Truncate long type definitions."""
        long_type = "| ".join([f"'value{i}'" for i in range(50)])
        content = f"type LongType = {long_type};"
        interfaces = extract_typescript_interfaces(content)
        type_def = [i for i in interfaces if "type LongType" in i][0]
        self.assertIn("...", type_def)


class TestExtractPythonInterfaces(unittest.TestCase):
    """Test Python interface extraction."""

    def test_function_definition(self):
        """Extract function definitions."""
        content = """
def greet(name: str) -> str:
    return f"Hello {name}"
        """
        interfaces = extract_python_interfaces(content)
        self.assertTrue(any("def greet" in i for i in interfaces))
        self.assertTrue(any("-> str" in i for i in interfaces))

    def test_function_without_return_type(self):
        """Extract function without return type annotation."""
        content = """
def process(data):
    return data.upper()
        """
        interfaces = extract_python_interfaces(content)
        self.assertTrue(any("def process" in i for i in interfaces))

    def test_async_function(self):
        """Extract async function definitions."""
        content = """
async def fetch_data(url: str) -> dict:
    pass
        """
        interfaces = extract_python_interfaces(content)
        # Note: current implementation doesn't handle async specifically
        self.assertTrue(any("def fetch_data" in i for i in interfaces))

    def test_class_definition(self):
        """Extract class definitions."""
        content = """
class UserService:
    def __init__(self):
        pass
        """
        interfaces = extract_python_interfaces(content)
        self.assertTrue(any("class UserService" in i for i in interfaces))

    def test_class_with_base(self):
        """Extract class with inheritance."""
        content = """
class AdminUser(User, PermissionMixin):
    pass
        """
        interfaces = extract_python_interfaces(content)
        self.assertTrue(any("class AdminUser" in i for i in interfaces))
        self.assertTrue(any("User, PermissionMixin" in i for i in interfaces))

    def test_method_extraction(self):
        """Extract methods from classes."""
        content = """
class Service:
    def process(self, data: dict) -> bool:
        return True
        """
        interfaces = extract_python_interfaces(content)
        self.assertTrue(any("def process" in i for i in interfaces))


class TestFormatMarkdown(unittest.TestCase):
    """Test markdown formatting."""

    def test_format_single_file(self):
        """Format single file result."""
        results = [{
            "path": "src/utils.ts",
            "interfaces": ["function add(a: number, b: number): number"],
            "line_count": 50
        }]
        output = format_markdown(results)
        self.assertIn("src/utils.ts", output)
        self.assertIn("function add", output)
        self.assertIn("50 lines", output)

    def test_format_with_error(self):
        """Format file with error."""
        results = [{
            "path": "missing.ts",
            "error": "File not found",
            "interfaces": []
        }]
        output = format_markdown(results)
        self.assertIn("Error", output)
        self.assertIn("File not found", output)

    def test_format_no_interfaces(self):
        """Format file with no extractable interfaces."""
        results = [{
            "path": "config.json",
            "interfaces": [],
            "line_count": 20
        }]
        output = format_markdown(results)
        self.assertIn("No extractable interfaces", output)


if __name__ == "__main__":
    unittest.main()
