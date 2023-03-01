#! python3

"""
Client to communicate with Jira.
"""

import asyncio
import logging
from typing import List, Optional, Union

from aiohttp import BasicAuth

from .httpclient import HttpClient

#: Create logger for this file.
logger = logging.getLogger()


class JiraClient:
    """
    This class is used to interfacing Jira server.
    """

    #: Version of Atlassian API used
    API_VERSION: int = 3

    #: Standard headers
    STANDARD_HEADERS: dict = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(
        self,
        jira_url: str,
        jira_username: str,
        jira_password: str,
    ):
        """
        Constructs the Jira client.

        :param jira_url: URL to connect to Jira.
        :param jira_username: Username to connect to Jira.
        :param jira_password: Password to connect to Jira.
        :raises Exception: If Jira credentials or URL are empty.
        """
        logger.debug("Create Jira client")

        if not jira_url:
            raise ValueError("Jira URL is invalid")
        if not jira_username:
            raise ValueError("Jira username is invalid")
        if not jira_password:
            raise ValueError("Jira password is invalid")

        self._http_client: HttpClient = HttpClient(
            jira_url.rstrip("/") + f"/rest/api/{self.API_VERSION}/",
            BasicAuth(jira_username, jira_password),
        )

        logger.debug("Jira client created")

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

    async def _get_paginated(
        self, suffix_url: str, headers: dict, query: dict, result_field: str
    ):
        """
        Send a GET request and aggregated the response.

        :param suffix_url: Last part of the URL contains the request.
        :param headers: Header for the request.
        :param query: Query of the request.
        :return: Response.
        """
        responses = []
        while True:
            response = await self._http_client.get(suffix_url, headers, query)
            responses += response[result_field]

            if query["startAt"] + query["maxResults"] >= response["total"]:
                break
            query["startAt"] += query["maxResults"]

        return responses

    async def validate_jql(self, jql: str):
        """
        Validate `jql` request.

        :param jql: JQL request to validate.
        """
        query = {"queries": [jql]}
        response = await self._http_client.post(
            "jql/parse", self.STANDARD_HEADERS, query
        )
        if "errors" in response["queries"][0]:
            raise ValueError(response["queries"][0]["errors"][0])

    async def tickets_from_jql(
        self, jql: str, fields: Optional[Union[List[str], str]] = None
    ) -> list:
        """
        Get tickets from a `jql` request.

        :param jql: JQL request to find tickets.
        :param fields: list of fields, for example: ['priority', 'summary']
        :return: Tickets list found.
        """
        if fields is None:
            fields = "*all"

        query = {
            "jql": jql,
            "fields": fields,
            "startAt": 0,
            "maxResults": 100,
        }
        return await self._get_paginated(
            "search", self.STANDARD_HEADERS, query, "issues"
        )

    async def changelogs(self, key: str) -> list:
        """
        Get all changelogs of a given ticket.

        :param key: Key of the ticket.
        :return: Changelogs list.
        """
        query = {
            "startAt": 0,
            "maxResults": 100,
        }
        return await self._get_paginated(
            f"issue/{key}/changelog", self.STANDARD_HEADERS, query, "values"
        )

    async def changelogs_from_tickets(self, tickets: list):
        """
        Get changelogs information from a list of `tickets`.

        :param tickets: List of tickets.
        :return: List of changelogs information.
        """
        tasks = []
        for ticket in tickets:
            task = asyncio.create_task(self.changelogs(ticket["key"]))
            tasks.append(task)

        return await asyncio.gather(*tasks)

    async def fields_information(self):
        """
        Get all fields information like id and associated display name.

        :return: List of fields information.
        """
        return await self._http_client.get("field", self.STANDARD_HEADERS)
