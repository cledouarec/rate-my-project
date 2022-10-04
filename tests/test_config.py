#! python3

"""
Unit tests for config.
"""

import os

import pytest

from rate_my_project.config import GlobalConfig, load_global_config


@pytest.fixture(autouse=True)
def secrets():
    """
    Set secrets as environment variables.
    """

    os.environ["ATLASSIAN_USER"] = "Username"
    os.environ["ATLASSIAN_TOKEN"] = "Token"


@pytest.fixture(scope="module")
def script_loc(request):
    """
    Return the directory of the currently running test script.
    """

    # uses .join instead of .dirname so we get a LocalPath object instead of
    # a string. LocalPath.join calls normpath for us when joining the path
    return request.fspath.join("..")


def test_yaml_basic_config(script_loc) -> None:
    """
    YAML basic config must be loaded without errors.
    """
    config = script_loc.join("../examples/basic_config.yaml")
    load_global_config(config)


def test_json_basic_config(script_loc) -> None:
    """
    JSON basic config must be loaded without errors.
    """
    config = script_loc.join("../examples/basic_config.json")
    load_global_config(config)


def test_yaml_multi_projects_config(script_loc) -> None:
    """
    YAML multi projects config must be loaded without errors.
    """
    config = script_loc.join("../examples/multi_projects_config.yaml")
    load_global_config(config)


def test_json_multi_projects_config(script_loc) -> None:
    """
    JSON multi projects config must be loaded without errors.
    """
    config = script_loc.join("../examples/multi_projects_config.json")
    load_global_config(config)


def test_yaml_multi_projects_with_anchor_config(script_loc) -> None:
    """
    YAML multi projects config with_anchor must be loaded without errors.
    """
    config = script_loc.join(
        "../examples/multi_projects_with_anchor_config.yaml"
    )
    load_global_config(config)


def test_config_with_empty_config() -> None:
    """
    An empty config must raise an exception.
    """
    with pytest.raises(Exception):
        GlobalConfig({})
