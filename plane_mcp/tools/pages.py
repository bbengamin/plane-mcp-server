"""Page-related tools for Plane MCP Server."""

from typing import Any

from fastmcp import FastMCP
from plane.models.pages import CreatePage, Page, UpdatePage

from plane_mcp.client import get_plane_client_context


def register_page_tools(mcp: FastMCP) -> None:
    """Register all page-related tools with the MCP server."""

    def update_page_via_sdk_resource(
        *,
        client: Any,
        endpoint: str,
        data: UpdatePage,
    ) -> Page:
        response = client.pages._patch(endpoint, data.model_dump(exclude_none=True))
        return Page.model_validate(response)

    def delete_page_via_sdk_resource(
        *,
        client: Any,
        endpoint: str,
    ) -> None:
        client.pages._delete(endpoint)

    @mcp.tool()
    def retrieve_workspace_page(
        page_id: str,
    ) -> Page:
        """
        Retrieve a workspace page by ID.

        Args:
            page_id: UUID of the page
            expand: Optional comma-separated list of fields to expand
            fields: Optional comma-separated list of fields to include

        Returns:
            Page object
        """
        client, workspace_slug = get_plane_client_context()

        return client.pages.retrieve_workspace_page(
            workspace_slug=workspace_slug,
            page_id=page_id,
        )

    @mcp.tool()
    def retrieve_project_page(
        project_id: str,
        page_id: str,
    ) -> Page:
        """
        Retrieve a project page by ID.

        Args:
            project_id: UUID of the project
            page_id: UUID of the page
            expand: Optional comma-separated list of fields to expand
            fields: Optional comma-separated list of fields to include

        Returns:
            Page object
        """
        client, workspace_slug = get_plane_client_context()

        return client.pages.retrieve_project_page(
            workspace_slug=workspace_slug,
            project_id=project_id,
            page_id=page_id,
        )

    @mcp.tool()
    def create_workspace_page(
        name: str,
        description_html: str,
        access: int | None = None,
        color: str | None = None,
        is_locked: bool | None = None,
        archived_at: str | None = None,
        view_props: dict[str, Any] | None = None,
        logo_props: dict[str, Any] | None = None,
        external_id: str | None = None,
        external_source: str | None = None,
    ) -> Page:
        """
        Create a workspace page.

        Args:
            name: Page name
            description_html: Page content in HTML format
            access: Access level for the page (integer)
            color: Page color
            is_locked: Whether the page is locked
            archived_at: Archive timestamp (ISO 8601 format)
            view_props: View properties dictionary
            logo_props: Logo properties dictionary
            external_id: External system identifier
            external_source: External system source name

        Returns:
            Created Page object
        """
        client, workspace_slug = get_plane_client_context()

        data = CreatePage(
            name=name,
            description_html=description_html,
            access=access,
            color=color,
            is_locked=is_locked,
            archived_at=archived_at,
            view_props=view_props,
            logo_props=logo_props,
            external_id=external_id,
            external_source=external_source,
        )

        return client.pages.create_workspace_page(
            workspace_slug=workspace_slug,
            data=data,
        )

    @mcp.tool()
    def create_project_page(
        project_id: str,
        name: str,
        description_html: str,
        access: int | None = None,
        color: str | None = None,
        is_locked: bool | None = None,
        archived_at: str | None = None,
        view_props: dict[str, Any] | None = None,
        logo_props: dict[str, Any] | None = None,
        external_id: str | None = None,
        external_source: str | None = None,
    ) -> Page:
        """
        Create a project page.

        Args:
            project_id: UUID of the project
            name: Page name
            description_html: Page content in HTML format
            access: Access level for the page (integer)
            color: Page color
            is_locked: Whether the page is locked
            archived_at: Archive timestamp (ISO 8601 format)
            view_props: View properties dictionary
            logo_props: Logo properties dictionary
            external_id: External system identifier
            external_source: External system source name

        Returns:
            Created Page object
        """
        client, workspace_slug = get_plane_client_context()

        data = CreatePage(
            name=name,
            description_html=description_html,
            access=access,
            color=color,
            is_locked=is_locked,
            archived_at=archived_at,
            view_props=view_props,
            logo_props=logo_props,
            external_id=external_id,
            external_source=external_source,
        )

        return client.pages.create_project_page(
            workspace_slug=workspace_slug,
            project_id=project_id,
            data=data,
        )

    @mcp.tool()
    def update_workspace_page(
        page_id: str,
        name: str | None = None,
        description_html: str | None = None,
        access: int | None = None,
        color: str | None = None,
        is_locked: bool | None = None,
        archived_at: str | None = None,
        view_props: dict[str, Any] | None = None,
        logo_props: dict[str, Any] | None = None,
        external_id: str | None = None,
        external_source: str | None = None,
    ) -> Page:
        """
        Update a workspace page by ID.

        Args:
            page_id: UUID of the page
            name: Page name
            description_html: Page content in HTML format
            access: Access level for the page (integer)
            color: Page color
            is_locked: Whether the page is locked
            archived_at: Archive timestamp (ISO 8601 format)
            view_props: View properties dictionary
            logo_props: Logo properties dictionary
            external_id: External system identifier
            external_source: External system source name

        Returns:
            Updated Page object
        """
        client, workspace_slug = get_plane_client_context()

        data = UpdatePage(
            name=name,
            description_html=description_html,
            access=access,
            color=color,
            is_locked=is_locked,
            archived_at=archived_at,
            view_props=view_props,
            logo_props=logo_props,
            external_id=external_id,
            external_source=external_source,
        )

        return update_page_via_sdk_resource(
            client=client,
            endpoint=f"{workspace_slug}/pages/{page_id}",
            data=data,
        )

    @mcp.tool()
    def update_project_page(
        project_id: str,
        page_id: str,
        name: str | None = None,
        description_html: str | None = None,
        access: int | None = None,
        color: str | None = None,
        is_locked: bool | None = None,
        archived_at: str | None = None,
        view_props: dict[str, Any] | None = None,
        logo_props: dict[str, Any] | None = None,
        external_id: str | None = None,
        external_source: str | None = None,
    ) -> Page:
        """
        Update a project page by ID.

        Args:
            project_id: UUID of the project
            page_id: UUID of the page
            name: Page name
            description_html: Page content in HTML format
            access: Access level for the page (integer)
            color: Page color
            is_locked: Whether the page is locked
            archived_at: Archive timestamp (ISO 8601 format)
            view_props: View properties dictionary
            logo_props: Logo properties dictionary
            external_id: External system identifier
            external_source: External system source name

        Returns:
            Updated Page object
        """
        client, workspace_slug = get_plane_client_context()

        data = UpdatePage(
            name=name,
            description_html=description_html,
            access=access,
            color=color,
            is_locked=is_locked,
            archived_at=archived_at,
            view_props=view_props,
            logo_props=logo_props,
            external_id=external_id,
            external_source=external_source,
        )

        return update_page_via_sdk_resource(
            client=client,
            endpoint=f"{workspace_slug}/projects/{project_id}/pages/{page_id}",
            data=data,
        )

    @mcp.tool()
    def delete_workspace_page(page_id: str) -> None:
        """
        Delete a workspace page by ID.

        Args:
            page_id: UUID of the page
        """
        client, workspace_slug = get_plane_client_context()
        delete_page_via_sdk_resource(
            client=client,
            endpoint=f"{workspace_slug}/pages/{page_id}",
        )

    @mcp.tool()
    def delete_project_page(project_id: str, page_id: str) -> None:
        """
        Delete a project page by ID.

        Args:
            project_id: UUID of the project
            page_id: UUID of the page
        """
        client, workspace_slug = get_plane_client_context()
        delete_page_via_sdk_resource(
            client=client,
            endpoint=f"{workspace_slug}/projects/{project_id}/pages/{page_id}",
        )
