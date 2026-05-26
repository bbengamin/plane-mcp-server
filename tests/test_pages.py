import asyncio
from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import ValidationError
from plane.errors.errors import HttpError

from plane_mcp.tools.pages import register_page_tools
import plane_mcp.tools.pages as page_tools


def extract_result(result):
    """Extract structured tool data from a FastMCP result."""
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
        return result[1]
    if hasattr(result, "structured_content") and result.structured_content is not None:
        return result.structured_content
    if hasattr(result, "structuredContent") and result.structuredContent is not None:
        return result.structuredContent
    if hasattr(result, "content") and result.content:
        return getattr(result.content[0], "text", None)
    return None


class FakePagesResource:
    def __init__(self):
        self.workspace_pages = {
            "workspace-page-1": {
                "id": "workspace-page-1",
                "name": "Workspace page",
                "description_html": "<p>Original workspace body</p>",
                "color": "#ff0000",
                "access": 0,
                "is_locked": False,
            }
        }
        self.project_pages = {
            ("project-1", "project-page-1"): {
                "id": "project-page-1",
                "name": "Project page",
                "description_html": "<p>Original project body</p>",
                "color": "#00ff00",
                "external_source": "agent-bridge",
                "is_locked": True,
            }
        }
        self.last_patch_payload = None

    def retrieve_workspace_page(self, workspace_slug: str, page_id: str):
        _ = workspace_slug
        if page_id not in self.workspace_pages:
            raise HttpError(
                "HTTP 404: Not Found",
                404,
                {"detail": f"Workspace page {page_id} not found"},
            )
        return deepcopy(self.workspace_pages[page_id])

    def retrieve_project_page(self, workspace_slug: str, project_id: str, page_id: str):
        _ = workspace_slug
        if not any(saved_project_id == project_id for saved_project_id, _ in self.project_pages):
            raise HttpError(
                "HTTP 404: Not Found",
                404,
                {"detail": f"Project {project_id} not found"},
            )

        key = (project_id, page_id)
        if key not in self.project_pages:
            raise HttpError(
                "HTTP 404: Not Found",
                404,
                {"detail": f"Project page {page_id} not found"},
            )
        return deepcopy(self.project_pages[key])

    def _patch(self, endpoint: str, data: dict):
        self.last_patch_payload = deepcopy(data)
        parts = endpoint.strip("/").split("/")

        if len(parts) == 3 and parts[1] == "pages":
            page_id = parts[2]
            if page_id not in self.workspace_pages:
                raise HttpError(
                    "HTTP 404: Not Found",
                    404,
                    {"detail": f"Workspace page {page_id} not found"},
                )
            self.workspace_pages[page_id].update(data)
            return deepcopy(self.workspace_pages[page_id])

        if len(parts) == 5 and parts[1] == "projects" and parts[3] == "pages":
            project_id = parts[2]
            page_id = parts[4]
            if not any(saved_project_id == project_id for saved_project_id, _ in self.project_pages):
                raise HttpError(
                    "HTTP 404: Not Found",
                    404,
                    {"detail": f"Project {project_id} not found"},
                )

            key = (project_id, page_id)
            if key not in self.project_pages:
                raise HttpError(
                    "HTTP 404: Not Found",
                    404,
                    {"detail": f"Project page {page_id} not found"},
                )
            self.project_pages[key].update(data)
            return deepcopy(self.project_pages[key])

        raise AssertionError(f"Unexpected patch endpoint: {endpoint}")


@contextmanager
def page_test_server():
    fake_pages = FakePagesResource()
    fake_client = SimpleNamespace(pages=fake_pages)
    with patch.object(
        page_tools,
        "get_plane_client_context",
        return_value=(fake_client, "test-workspace"),
    ):
        mcp = FastMCP("test-pages")
        register_page_tools(mcp)
        yield mcp, fake_pages


class TestPageTools(unittest.TestCase):
    def test_update_page_tools_are_listed(self):
        async def run():
            with page_test_server() as (mcp, _fake_pages):
                tools = await mcp._list_tools_mcp()
                tool_names = {tool.name for tool in tools}

            self.assertIn("update_workspace_page", tool_names)
            self.assertIn("update_project_page", tool_names)

        asyncio.run(run())

    def test_update_workspace_page_updates_title_and_body_without_clearing_omitted_fields(self):
        async def run():
            with page_test_server() as (mcp, fake_pages):
                result = await mcp._call_tool_mcp(
                    "update_workspace_page",
                    {
                        "page_id": "workspace-page-1",
                        "name": "Updated workspace page",
                        "description_html": "<p>Updated workspace body</p>",
                    },
                )
                updated_page = extract_result(result)

                self.assertEqual(updated_page["name"], "Updated workspace page")
                self.assertEqual(updated_page["description_html"], "<p>Updated workspace body</p>")
                self.assertEqual(
                    fake_pages.last_patch_payload,
                    {
                        "name": "Updated workspace page",
                        "description_html": "<p>Updated workspace body</p>",
                    },
                )

                retrieved = extract_result(
                    await mcp._call_tool_mcp(
                        "retrieve_workspace_page",
                        {"page_id": "workspace-page-1"},
                    )
                )
                self.assertEqual(retrieved["color"], "#ff0000")
                self.assertEqual(retrieved["access"], 0)

        asyncio.run(run())

    def test_update_project_page_updates_title_and_body_without_clearing_omitted_fields(self):
        async def run():
            with page_test_server() as (mcp, fake_pages):
                result = await mcp._call_tool_mcp(
                    "update_project_page",
                    {
                        "project_id": "project-1",
                        "page_id": "project-page-1",
                        "name": "Updated project page",
                        "description_html": "<p>Updated project body</p>",
                    },
                )
                updated_page = extract_result(result)

                self.assertEqual(updated_page["name"], "Updated project page")
                self.assertEqual(updated_page["description_html"], "<p>Updated project body</p>")
                self.assertEqual(
                    fake_pages.last_patch_payload,
                    {
                        "name": "Updated project page",
                        "description_html": "<p>Updated project body</p>",
                    },
                )

                retrieved = extract_result(
                    await mcp._call_tool_mcp(
                        "retrieve_project_page",
                        {
                            "project_id": "project-1",
                            "page_id": "project-page-1",
                        },
                    )
                )
                self.assertEqual(retrieved["color"], "#00ff00")
                self.assertEqual(retrieved["external_source"], "agent-bridge")

        asyncio.run(run())

    def test_update_page_tools_require_ids(self):
        cases = [
            ("update_workspace_page", {"name": "Updated workspace page"}, "page_id"),
            (
                "update_project_page",
                {"page_id": "project-page-1", "name": "Updated project page"},
                "project_id",
            ),
            (
                "update_project_page",
                {"project_id": "project-1", "name": "Updated project page"},
                "page_id",
            ),
        ]

        async def run():
            with page_test_server() as (mcp, _fake_pages):
                for tool_name, arguments, expected_message in cases:
                    with self.subTest(tool_name=tool_name, arguments=arguments):
                        with self.assertRaisesRegex(ValidationError, expected_message):
                            await mcp._call_tool_mcp(tool_name, arguments)

        asyncio.run(run())

    def test_update_page_tools_surface_invalid_ids(self):
        cases = [
            (
                "update_workspace_page",
                {"page_id": "missing-workspace-page", "name": "Updated workspace page"},
                "Workspace page missing-workspace-page not found",
            ),
            (
                "update_project_page",
                {
                    "project_id": "missing-project",
                    "page_id": "project-page-1",
                    "name": "Updated project page",
                },
                "Project missing-project not found",
            ),
            (
                "update_project_page",
                {
                    "project_id": "project-1",
                    "page_id": "missing-project-page",
                    "name": "Updated project page",
                },
                "Project page missing-project-page not found",
            ),
        ]

        async def run():
            with page_test_server() as (mcp, _fake_pages):
                for tool_name, arguments, expected_message in cases:
                    with self.subTest(tool_name=tool_name, arguments=arguments):
                        with self.assertRaisesRegex(ToolError, expected_message):
                            await mcp._call_tool_mcp(tool_name, arguments)

        asyncio.run(run())
