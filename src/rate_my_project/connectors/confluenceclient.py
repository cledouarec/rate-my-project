#! python3

"""
Client to communicate with Confluence.
"""

import logging
from typing import List

from aiohttp import BasicAuth

from .httpclient import HttpClient

#: Create logger for this file.
logger = logging.getLogger()


class ConfluenceClient:
    """
    This class is used to interfacing Confluence server.
    """

    #: Standard headers
    STANDARD_HEADERS: dict = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    #: No check headers
    NO_CHECK_HEADERS: dict = {
        "X-Atlassian-Token": "no-check",
    }

    def __init__(
        self,
        confluence_url: str,
        confluence_username: str,
        confluence_password: str,
    ):
        """
        Constructs the Confluence client.

        :param confluence_url: URL to connect to Confluence.
        :param confluence_username: Username to connect to Confluence.
        :param confluence_password: Password to connect to Confluence.
        :raises Exception: If URL, username or password are invalids.
        """
        logger.debug("Create Confluence client")

        if not confluence_url:
            raise Exception("Confluence URL is invalid")
        if not confluence_username:
            raise Exception("Confluence username is invalid")
        if not confluence_password:
            raise Exception("Confluence password is invalid")

        self._http_client: HttpClient = HttpClient(
            confluence_url.rstrip("/") + "/wiki/rest/api/",
            BasicAuth(confluence_username, confluence_password),
        )

        logger.debug("Confluence client created")

    async def __aenter__(self):
        """
        Create session to send requests.
        """
        await self._http_client.__aenter__()
        return self

    async def __aexit__(self, *err):
        """
        Close session.
        """
        await self._http_client.__aexit__(*err)

    async def get_page_content(self, space: str, title: str) -> dict:
        """
        Get a page content from `title` in the `space`.

        :param space: Confluence space.
        :param title: Page title.
        :return: Content if page is found.
        """
        query = {
            "spaceKey": space,
            "title": title,
        }
        response = await self._http_client.get(
            "content", self.STANDARD_HEADERS, query
        )
        if not response["results"]:
            raise Exception("Page not found")
        return response["results"][0]

    async def get_page_content_id(self, space: str, title: str) -> int:
        """
        Get a page content identifier from `title` in the `space`.

        :param space: Confluence space.
        :param title: Page title.
        :return: Identifier of the page.
        """
        response = await self.get_page_content(space, title)
        return response["id"]

    async def get_page_content_version(self, space: str, title: str) -> int:
        """
        Get a page content version from `title` in the `space`.

        :param space: Confluence space.
        :param title: Page title.
        :return: Version of the page.
        """
        page_id = await self.get_page_content_id(space, title)
        response = await self._http_client.get(
            f"content/{page_id}/history", self.STANDARD_HEADERS
        )
        return response["lastUpdated"]["number"]

    async def create_or_update_page(
        self,
        space: str,
        parent_page: str,
        title: str,
        message: str,
        representation="wiki",
    ) -> None:
        """
        Create or update page in Confluence in the given `space`. The page will
        be located under the `parent_page` and will have the given `title` and
        content `message` in given `representation` format. By default,
        Wiki markup format is used but "storage" can also be used.

        :param space: Confluence space.
        :param parent_page: Name of the parent page.
        :param title: Page title.
        :param message: Page message.
        :param representation: Content format (wiki or storage).
        :raises Exception: If parent page is not found.
        """
        logger.debug("Create or update page")

        if representation not in ["storage", "wiki"]:
            raise ValueError("Wrong value for representation")

        parent_id = await self.get_page_content_id(space, parent_page)

        query = {
            "type": "page",
            "title": title,
            "space": {"key": space},
            "ancestors": [{"id": parent_id}],
            "body": {
                representation: {
                    "value": message,
                    "representation": representation,
                }
            },
        }

        update = False
        try:
            page_id = await self.get_page_content_id(space, title)
            query["id"] = str(page_id)
            update = True
        except Exception:
            pass

        if update:
            version = await self.get_page_content_version(space, title)
            query["version"] = {"number": version + 1}
            await self._http_client.put(
                f"content/{query['id']}",
                self.STANDARD_HEADERS,
                query,
            )
            logger.debug("Page updated")
        else:
            await self._http_client.post(
                "content", self.STANDARD_HEADERS, query
            )
            logger.debug("New page created")

    async def upload_files(
        self,
        space: str,
        title: str,
        filenames: List[str],
    ):
        """
        Upload files and attach to the page with given `title` in the `space`.

        :param space: Confluence space.
        :param title: Page title.
        :param filenames: List of file to upload.
        """
        page_id = await self.get_page_content_id(space, title)
        for filename in filenames:
            with open(filename, "rb") as file:
                query = {
                    "type": "attachment",
                    "minorEdit": "true",
                    "file": file,
                }

                await self._http_client.put(
                    f"content/{page_id}/child/attachment",
                    self.NO_CHECK_HEADERS,
                    data=query,
                )
