import asyncio
from types import SimpleNamespace

from plane_mcp.server import get_stdio_mcp
from plane_mcp.tools import pages as page_tools


class FakePagesResource:
    def __init__(self):
        self.patch_calls = []
        self.delete_calls = []

    def _patch(self, endpoint, data):
        self.patch_calls.append((endpoint, data))
        return {
            "id": "page-123",
            "name": data.get("name"),
            "description_html": data.get("description_html"),
        }

    def _delete(self, endpoint):
        self.delete_calls.append(endpoint)


def get_tool_fn(name: str):
    async def load_tool():
        mcp = get_stdio_mcp()
        tool = await mcp._tool_manager.get_tool(name)
        return tool.fn

    return asyncio.run(load_tool())


def test_page_tools_list_includes_update_and_delete():
    async def list_tool_names():
        mcp = get_stdio_mcp()
        tools = await mcp._list_tools_mcp()
        return {tool.name for tool in tools}

    tool_names = asyncio.run(list_tool_names())

    assert "update_workspace_page" in tool_names
    assert "update_project_page" in tool_names
    assert "delete_workspace_page" in tool_names
    assert "delete_project_page" in tool_names


def test_update_workspace_page_uses_pages_patch(monkeypatch):
    fake_pages = FakePagesResource()
    fake_client = SimpleNamespace(pages=fake_pages)
    monkeypatch.setattr(
        page_tools,
        "get_plane_client_context",
        lambda: (fake_client, "workspace-slug"),
    )

    update_workspace_page = get_tool_fn("update_workspace_page")
    result = update_workspace_page(
        page_id="page-123",
        name="Updated workspace page",
        description_html="<p>Updated</p>",
    )

    assert fake_pages.patch_calls == [
        (
            "workspace-slug/pages/page-123",
            {"name": "Updated workspace page", "description_html": "<p>Updated</p>"},
        )
    ]
    assert result.id == "page-123"
    assert result.name == "Updated workspace page"


def test_update_project_page_uses_pages_patch(monkeypatch):
    fake_pages = FakePagesResource()
    fake_client = SimpleNamespace(pages=fake_pages)
    monkeypatch.setattr(
        page_tools,
        "get_plane_client_context",
        lambda: (fake_client, "workspace-slug"),
    )

    update_project_page = get_tool_fn("update_project_page")
    result = update_project_page(
        project_id="project-456",
        page_id="page-123",
        name="Updated project page",
    )

    assert fake_pages.patch_calls == [
        (
            "workspace-slug/projects/project-456/pages/page-123",
            {"name": "Updated project page"},
        )
    ]
    assert result.id == "page-123"
    assert result.name == "Updated project page"


def test_delete_workspace_page_uses_pages_delete(monkeypatch):
    fake_pages = FakePagesResource()
    fake_client = SimpleNamespace(pages=fake_pages)
    monkeypatch.setattr(
        page_tools,
        "get_plane_client_context",
        lambda: (fake_client, "workspace-slug"),
    )

    delete_workspace_page = get_tool_fn("delete_workspace_page")
    result = delete_workspace_page(page_id="page-123")

    assert fake_pages.delete_calls == ["workspace-slug/pages/page-123"]
    assert result is None


def test_delete_project_page_uses_pages_delete(monkeypatch):
    fake_pages = FakePagesResource()
    fake_client = SimpleNamespace(pages=fake_pages)
    monkeypatch.setattr(
        page_tools,
        "get_plane_client_context",
        lambda: (fake_client, "workspace-slug"),
    )

    delete_project_page = get_tool_fn("delete_project_page")
    result = delete_project_page(project_id="project-456", page_id="page-123")

    assert fake_pages.delete_calls == ["workspace-slug/projects/project-456/pages/page-123"]
    assert result is None
