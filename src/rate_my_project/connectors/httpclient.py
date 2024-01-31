#! python3

"""
Client to communicate with Http.
"""

import logging
from typing import Any, Optional

from aiohttp import BasicAuth, ClientSession, TCPConnector

#: Create logger for this file.
logger = logging.getLogger()


class HttpClient:
    """
    This class is used to interfacing Http server.
    """

    def __init__(
        self,
        http_url: str,
        auth: Optional[BasicAuth] = None,
    ):
        """
        Constructs the Http client.

        :param http_url: URL to connect to Http server.
        :param auth: Authentication to connect to server.
        :raises Exception: If URL is empty.
        """
        logger.debug("Create Http client")

        if not http_url:
            raise ValueError("Http URL is invalid")
        self._url: str = http_url

        #: Server authentication
        self._auth: Optional[BasicAuth] = auth

        #: HTTP session
        self._session: Optional[ClientSession] = None

        logger.debug("Http client created")

    async def __aenter__(self):
        """
        Create Http session to send multiple requests.
        """
        self._session = ClientSession(
            auth=self._auth,
            raise_for_status=True,
            connector=TCPConnector(limit=50),
        )
        return self

    async def __aexit__(self, *err):
        """
        Close Http session.
        """
        await self._session.close()
        self._session = None

    async def get(self, suffix_url: str, headers: dict, query: Any = None):
        """
        Send a GET request.

        :param suffix_url: Last part of the URL contains the request.
        :param headers: Header for the request.
        :param query: Query of the request.
        :return: Response.
        """
        if self._session:
            async with self._session.get(
                url=self._url + suffix_url,
                headers=headers,
                params=query,
            ) as response:
                return await response.json()
        else:
            async with ClientSession(
                auth=self._auth,
                raise_for_status=True,
                connector=TCPConnector(limit=50),
            ) as session:
                async with session.get(
                    url=self._url + suffix_url,
                    headers=headers,
                    params=query,
                ) as response:
                    return await response.json()

    async def post(
        self,
        suffix_url: str,
        headers: dict,
        json: Any = None,
        data: Any = None,
    ):
        """
        Send a POST request.

        :param suffix_url: Last part of the URL contains the request.
        :param headers: Header for the request.
        :param json: JSON payload of the request.
        :param data: Payload of the request.
        :return: Response.
        """
        if self._session:
            async with self._session.post(
                url=self._url + suffix_url,
                data=data,
                json=json,
                headers=headers,
            ) as response:
                return await response.json()
        else:
            async with ClientSession(
                auth=self._auth,
                raise_for_status=True,
                connector=TCPConnector(limit=50),
            ) as session:
                async with session.post(
                    url=self._url + suffix_url,
                    data=data,
                    json=json,
                    headers=headers,
                ) as response:
                    return await response.json()

    async def put(
        self,
        suffix_url: str,
        headers: dict,
        json: Any = None,
        data: Any = None,
    ):
        """
        Send a PUT request.

        :param suffix_url: Last part of the URL contains the request.
        :param headers: Header for the request.
        :param json: JSON payload of the request.
        :param data: Payload of the request.
        :return: Response.
        """
        if self._session:
            async with self._session.put(
                url=self._url + suffix_url,
                data=data,
                json=json,
                headers=headers,
            ) as response:
                return await response.json()
        else:
            async with ClientSession(
                auth=self._auth,
                raise_for_status=True,
                connector=TCPConnector(limit=50),
            ) as session:
                async with session.put(
                    url=self._url + suffix_url,
                    data=data,
                    json=json,
                    headers=headers,
                ) as response:
                    return await response.json()
