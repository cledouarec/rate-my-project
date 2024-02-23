#! python3

"""
Helper functions.
"""

import logging

import inflection

from .connectors import JiraClient

#: Create logger for this file.
logger = logging.getLogger()


async def fetch_tickets_information(
    jira_client: JiraClient, jql: str
) -> tuple:
    """
    Fetch tickets and associated changelogs information from `JQL` query.

    TODO The fields list will be fetched to retrieve custom fields if needed.

    :param jira_client: Jira client to retrieve tickets information.
    :param jql: JQL query.
    :return: Tickets, changelogs and parents tickets.
    """
    async with jira_client as jira_session:
        tickets = await jira_session.tickets_from_jql(jql)
        changelogs = await jira_session.changelogs_from_tickets(tickets)
        parents = await jira_session.parents_from_tickets(tickets)
        # fields = await jira_session.fields_information()
        return tickets, changelogs, parents


def to_snake_case(text: str) -> str:
    """
    Convert test to snake case.

    :param text: Input text to convert.
    :return: Text in snake case.
    """
    # underscore function do not replace the space
    return inflection.underscore(text.replace(" ", "_"))
