#! python3

"""
Manage configuration file.
"""

from dataclasses import dataclass
import logging
from typing import List, Optional

from pydantic import BaseModel, BaseSettings, Field, HttpUrl, SecretStr
from pydantic_yaml import YamlModel

from .connectors import ConfluenceClient, JiraClient

#: Create logger for this file.
logger = logging.getLogger()


class Secrets(BaseSettings):
    """
    This class is used to store all secrets from environment variables.
    """

    #: Username for Jira/Confluence
    user: str = Field(env="ATLASSIAN_USER")
    #: Token for Jira/Confluence
    token: SecretStr = Field(env="ATLASSIAN_TOKEN")

    class Config:
        """
        Specific configuration.
        """

        allow_mutation = False
        env_file = ".env"
        env_file_encoding = "utf-8"


class Server(BaseModel):
    """
    This class is used to store server configuration.
    """

    #: Jira URL
    jira: HttpUrl = Field(alias="Jira")

    #: Confluence URL
    confluence: HttpUrl = Field(alias="Confluence")

    class Config:
        """
        Specific configuration.
        """

        allow_mutation = False


class Fields(BaseModel):
    """
    This class is used to store fields configuration.
    """

    #: Project name
    sprint: str = Field(alias="Sprint")
    #: Query to retrieve tickets
    story_points: str = Field(alias="Story points")

    class Config:
        """
        Specific configuration.
        """

        allow_mutation = False


class Report(BaseModel):
    """
    This class is used to store report configuration.
    """

    #: Confluence output space.
    space: str = Field(alias="Space")
    #: Confluence parent page.
    parent_page: str = Field(alias="Parent page")
    #: Page template to use.
    template: Optional[str] = Field("report.jinja2", alias="Template")

    class Config:
        """
        Specific configuration.
        """

        allow_mutation = False


class WorkflowState(BaseModel):
    """
    This class is used to store report configuration.
    """

    #: Workflow state name.
    name: str = Field(alias="Name")
    #: Workflow state status to map.
    status: List[str] = Field(alias="Status")
    #: Start tag associated to this workflow state to compute lead time.
    start: Optional[bool] = Field(False, alias="Start")
    #: Stop tag associated to this workflow state to compute lead time.
    stop: Optional[bool] = Field(False, alias="Stop")

    class Config:
        """
        Specific configuration.
        """

        allow_mutation = False


class Project(BaseModel):
    """
    This class is used to store project configuration.
    """

    #: Project name
    name: str = Field(alias="Name")
    #: Query to retrieve tickets
    jql: str = Field(alias="JQL")
    #: Report configuration.
    report: Report = Field(alias="Report")
    # Workflow configuration.
    workflow: List[WorkflowState] = Field(alias="Workflow")

    class Config:
        """
        Specific configuration.
        """

        allow_mutation = False

    def workflow_to_dict(self) -> list:
        """
        Returns the workflow configuration in list of dictionary.

        :return: Configuration string in JSON format.
        """
        return [workflow.dict() for workflow in self.workflow]


class Config(YamlModel):
    """
    This class is used to store main configuration excepted secrets.
    """

    #: Server configuration.
    server: Server = Field(alias="Server")
    #: Fields configuration
    fields: Fields = Field(alias="Fields")
    #: List of all projects
    projects: List[Project] = Field(alias="Projects")

    class Config:
        """
        Specific configuration.
        """

        allow_mutation = False


@dataclass
class GlobalConfig:
    """
    Global configuration.
    """

    #: Secrets configuration.
    secrets: Secrets
    # Main configuration.
    config: Config

    def json(self) -> str:
        """
        Returns the configuration in json format.

        :return: Configuration string in JSON format.
        """
        return f"""
        {
            {
                "secrets": {self.secrets.json()},
                "config": {self.config.json()}
            }
        }"""

    def confluence_client(self) -> ConfluenceClient:
        """
        Create and return a Jira client.

        :return: Jira client.
        """
        return ConfluenceClient(
            self.config.server.confluence,
            self.secrets.user,
            self.secrets.token.get_secret_value(),
        )

    def jira_client(self) -> JiraClient:
        """
        Create and return a Jira client.

        :return: Jira client.
        """
        return JiraClient(
            self.config.server.jira,
            self.secrets.user,
            self.secrets.token.get_secret_value(),
        )


def load_global_config(config_file: str) -> GlobalConfig:
    """
    Loads the configuration file (JSON or YAML) and the secrets.

    :param config_file: Configuration file to parse.
    :return: Configuration parsed.
    :raises Exception: If configuration extension file is unknown (.json,
    .yaml, .yml).
    :raises ValidationError: If configuration is invalid.
    """
    with open(config_file, encoding="utf-8") as file:
        return GlobalConfig(Secrets(), Config.parse_raw(file.read()))
