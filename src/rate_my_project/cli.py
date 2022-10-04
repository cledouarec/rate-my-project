#! python3

"""
Manage command line interface.
"""

import logging
import sys

import click
from pydantic import ValidationError

from .config import load_global_config
from .dashboard import start_web_application
from .report import generate_all_reports


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
def cli(verbose: bool = False) -> None:
    """
    Swiss knife for measuring project efficiency.
    """
    # Create logger
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Create logger
    logging.basicConfig(
        stream=sys.stdout,
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=log_level,
    )


@cli.command()
@click.argument("config", type=click.Path(exists=True))
def report(config) -> None:
    """
    Generate report from CONFIG file.
    """
    # Get configuration from JSON/YAML file
    try:
        global_config = load_global_config(config)
    except ValidationError as error:
        sys.exit(str(error))

    logging.getLogger().debug(global_config.json())
    generate_all_reports(global_config)


@cli.command()
@click.argument("config", type=click.Path(exists=True))
def explore(config) -> None:
    """
    Explore efficiency metrics with web interface from CONFIG file.
    """
    # Get configuration from JSON/YAML file
    try:
        global_config = load_global_config(config)
    except ValidationError as error:
        sys.exit(str(error))

    logging.getLogger().debug(global_config.json())
    start_web_application(global_config)
