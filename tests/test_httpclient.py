#! python3

"""
Unit tests for httpclient.
"""

import pytest
from aiohttp import BasicAuth

from rate_my_project.connectors import HttpClient


def test_create_http_client_with_empty_url() -> None:
    """
    Http client creation with invalid url must raise an exception.
    """
    with pytest.raises(Exception):
        HttpClient("", BasicAuth("user", "pass"))


def test_create_jira_client_with_empty_username() -> None:
    """
    Http client creation with no authentication must not raise an exception.
    """
    HttpClient("http://test", None)
