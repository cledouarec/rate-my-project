#! python3

"""
Unit tests for jiraclient.
"""

import pytest

from rate_my_project.connectors import JiraClient


def test_create_jira_client_with_empty_url() -> None:
    """
    Jira client creation with invalid url must raise an exception.
    """
    with pytest.raises(Exception):
        JiraClient("", "user", "pass")


def test_create_jira_client_with_empty_authentication() -> None:
    """
    Jira client creation with invalid url must raise an exception.
    """
    with pytest.raises(Exception):
        JiraClient("http://test", "", "pass")


def test_create_jira_client_with_empty_password() -> None:
    """
    Jira client creation with invalid password must raise an exception.
    """
    with pytest.raises(Exception):
        JiraClient("http://test", "user", "")
