#! python3

"""
Manage configuration file.
"""

from dataclasses import dataclass
import json
import logging
import pathlib
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

from .connectors import ConfluenceClient, JiraClient

#: Create logger for this file.
logger = logging.getLogger()


class Secrets(BaseSettings):
    """
    This class is used to store all secrets from environment variables.
    """

    #: Specific configuration
    model_config = SettingsConfigDict(
        frozen=False, env_file=".env", env_file_encoding="utf-8"
    )

    #: Username for Jira/Confluence
    user: str = Field(alias="ATLASSIAN_USER")
    #: Token for Jira/Confluence
    token: SecretStr = Field(alias="ATLASSIAN_TOKEN")


class ImmutableModel(BaseModel):
    """
    This class is used to have immutable model. It is used as base madel.
    """

    #: Specific configuration
    model_config = ConfigDict(frozen=False)


class Server(ImmutableModel):
    """
    This class is used to store server configuration.
    """

    #: Jira URL
    jira: HttpUrl

    #: Confluence URL
    confluence: HttpUrl


class Fields(ImmutableModel):
    """
    This class is used to store fields configuration.
    """

    #: Project name
    sprint: str
    #: Query to retrieve tickets
    story_points: str


class Report(ImmutableModel):
    """
    This class is used to store report configuration.
    """

    #: Confluence output space.
    space: str
    #: Confluence parent page.
    parent_page: str
    #: Page template to use.
    template: Optional[str] = Field("report.jinja2")


class WorkflowState(ImmutableModel):
    """
    This class is used to store report configuration.
    """

    #: Workflow state name.
    name: str
    #: Workflow state status to map.
    status: List[str]
    #: Start tag associated to this workflow state to compute lead time.
    start: Optional[bool] = Field(False)
    #: Stop tag associated to this workflow state to compute lead time.
    stop: Optional[bool] = Field(False)


class Project(ImmutableModel):
    """
    This class is used to store project configuration.
    """

    #: Project name
    name: str
    #: Query to retrieve tickets
    jql: str
    #: Report configuration.
    report: Report
    #: Workflow configuration.
    workflow: List[WorkflowState]

    def workflow_to_dict(self) -> list:
        """
        Returns the workflow configuration in list of dictionary.

        :return: Configuration string in JSON format.
        """
        return [workflow.model_dump() for workflow in self.workflow]


class Config(ImmutableModel):
    """
    This class is used to store main configuration excepted secrets.
    """

    #: Server configuration.
    server: Server
    #: Fields configuration
    fields: Fields
    #: List of all projects
    projects: List[Project]


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
                "secrets": {self.secrets.model_dump_json()},
                "config": {self.config.model_dump_json()}
            }
        }"""

    def confluence_client(self) -> ConfluenceClient:
        """
        Create and return a Jira client.

        :return: Jira client.
        """
        return ConfluenceClient(
            str(self.config.server.confluence),
            self.secrets.user,
            self.secrets.token.get_secret_value(),
        )

    def jira_client(self) -> JiraClient:
        """
        Create and return a Jira client.

        :return: Jira client.
        """
        return JiraClient(
            str(self.config.server.jira),
            self.secrets.user,
            self.secrets.token.get_secret_value(),
        )


def _parse_yaml_config(yaml_config_file: str) -> dict:
    """
    Constructs the configuration from YAML file.

    :param yaml_config_file: YAML configuration file to parse.
    :raises Exception: If configuration file is invalid.
    """
    logger.info("Parse YAML configuration from %s", yaml_config_file)

    try:
        with open(yaml_config_file, encoding="utf-8") as yaml_config:
            return yaml.safe_load(yaml_config)
    except Exception as error:
        raise Exception("Failed to parse YAML configuration") from error


def _parse_json_config(json_config_file: str) -> dict:
    """
    Constructs the configuration from JSON file.

    :param json_config_file: JSON configuration file to parse.
    :raises Exception: If configuration file is invalid.
    """
    logger.info("Parse JSON configuration from %s", json_config_file)

    try:
        with open(json_config_file, encoding="utf-8") as json_config:
            return json.load(json_config)
    except Exception as error:
        raise Exception("Failed to parse JSON configuration") from error


def load_global_config(config_file: str) -> GlobalConfig:
    """
    Loads the configuration file (JSON or YAML) and the secrets.

    :param config_file: Configuration file to parse.
    :return: Configuration parsed.
    :raises Exception: If configuration extension file is unknown (.json,
    .yaml, .yml).
    :raises ValidationError: If configuration is invalid.
    """
    config_type = pathlib.Path(config_file).suffix
    if config_type in [".yaml", ".yml"]:
        config = _parse_yaml_config(config_file)
    elif config_type == ".json":
        config = _parse_json_config(config_file)
    else:
        raise Exception("Unknown file extension for configuration")
    return GlobalConfig(Secrets(), Config.model_validate(config))
