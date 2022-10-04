#! python3

"""
Module of all connectors used to collect or write data.
"""

from .confluenceclient import ConfluenceClient
from .httpclient import HttpClient
from .jiraclient import JiraClient

__all__ = ["ConfluenceClient", "HttpClient", "JiraClient"]
