#! python3

"""
Common metric interface.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import importlib
import logging
import os
from typing import List, Optional

from dash import dcc
import dash_bootstrap_components as dbc
from dateutil.parser import isoparse
import pandas as pd
import plotly.graph_objects as go

#: Create logger for this file.
logger = logging.getLogger()


@dataclass
class MetricData:
    """
    This class is used to store all the tickets information used to produce
    metrics and analysis.
    """

    #: Raw data in case of advanced or custom processing needed
    raw: tuple

    #: Basics information like title, reporter, type, nb sprint, etc
    info: pd.DataFrame

    #: Information which change during time like status, assignee, etc
    changes: pd.DataFrame

    #: Workflow of the project
    workflow: list

    @classmethod
    def from_tickets_and_changelogs(
        cls,
        fields: dict,
        workflow: list,
        tickets: list,
        tickets_changelogs: list,
        tickets_parents: list,
    ) -> MetricData:
        """
        Create data for metric from `tickets` and `changelogs` information.

        :param fields: Dictionary of fields to retrieve.
        :param workflow: List of state in the workflow.
        :param tickets: List of tickets information.
        :param tickets_changelogs: List of changelogs associated to tickets.
        :param tickets_parents: List of parent tickets associated to tickets.
        :return: Data for metric.
        """
        logger.debug("Create data for metric from tickets and changelogs")

        raw = (fields, workflow, tickets, tickets_changelogs, tickets_parents)

        tickets_info = []
        tickets_changes = []
        status_backlog = cls._map_status_from_workflow("Backlog", workflow)

        for ticket, changelogs in zip(tickets, tickets_changelogs):
            key = ticket["key"]
            sprints = ticket["fields"].get(fields["sprint"])
            if not sprints:
                sprints = []

            fix_versions = []
            for fix_version in ticket["fields"]["fixVersions"]:
                fix_versions.append(fix_version["name"])

            parent = None
            if ticket["fields"].get("parent"):
                parent = ticket["fields"]["parent"]["key"]

            tickets_info.append(
                {
                    "key": key,
                    "type": ticket["fields"]["issuetype"]["name"],
                    "summary": ticket["fields"]["summary"],
                    "reporter": ticket["fields"]["reporter"]["displayName"],
                    "story point": ticket["fields"].get(
                        fields["story_points"]
                    ),
                    "sprints": len(sprints),
                    "versions": fix_versions,
                    "parent": parent,
                }
            )
            assignee = "Unassigned"
            status = status_backlog
            tickets_changes.append(
                {
                    "key": key,
                    "date": isoparse(ticket["fields"]["created"]),
                    "assignee": assignee,
                    "status": status,
                }
            )

            for changelog in changelogs:
                for change in changelog["items"]:
                    change_type = change.get("fieldId")
                    if not change_type:
                        continue
                    if change_type == "assignee":
                        if change["toString"]:
                            assignee = change["toString"]
                        else:
                            assignee = "Unassigned"
                    elif change_type == "status":
                        status = cls._map_status_from_workflow(
                            change["toString"], workflow
                        )
                    else:
                        continue

                    tickets_changes.append(
                        {
                            "key": key,
                            "date": isoparse(changelog["created"]),
                            "assignee": assignee,
                            "status": status,
                        }
                    )

        tickets_info_df = pd.DataFrame.from_records(tickets_info, index="key")
        tickets_changes_df = pd.DataFrame.from_records(tickets_changes)
        tickets_changes_df["date"] = pd.to_datetime(
            tickets_changes_df["date"], utc=True
        )
        status_order = pd.CategoricalDtype(
            categories=[state["name"] for state in workflow], ordered=True
        )
        tickets_changes_df["status"] = tickets_changes_df["status"].astype(
            status_order
        )

        logger.debug("Data for metric created")
        return cls(raw, tickets_info_df, tickets_changes_df, workflow)

    @staticmethod
    def _map_status_from_workflow(status: str, workflow: list) -> str:
        """
        Search the `status` associated in the `workflow` and map to the state
        name. If the `status` is not associated to a state, it returns the
        given `status` in input.

        :param status: Status to map.
        :param workflow: List of state in the workflow.
        :return: Status name.
        """
        for state in workflow:
            if status in state["status"]:
                return state["name"]
        return status


@dataclass
class MetricReport:
    """
    This class is used to store all the information used to produce report
    of the metric.
    """

    #: Name of the metric. Used to retrieve template associated.
    metric_name: str

    #: List of the figures to include in the report.
    figures: List[str]

    #: Additional data used to generate report.
    report_data: Optional[dict] = None


class Metric(ABC):
    """
    This class is used to provide an interface for all metrics.
    """

    #: Define output directory.
    OUTPUT_DIR: str = "out"

    @abstractmethod
    def compute_dashboard(self, data: MetricData) -> List[dbc.Row]:
        """
        Interface to compute widget of the dashboard related to this metric.

        :param data: Metric input data.
        :return: Dash widgets.
        """

    @abstractmethod
    def compute_report(self, data: MetricData) -> MetricReport:
        """
        Interface to compute widget of the report related to this metric.

        :param data: Metric input data.
        :return: Report of the metric.
        """

    @staticmethod
    def _draw_figure(title: str, figure: go.Figure) -> dbc.Col:
        """
        Helper function to set a graph in a common layout.

        :param title: Title of the graph.
        :param figure: Graph.
        :return: Dash widgets.
        """
        figure.update_traces(
            hoverinfo="label+percent", textinfo="value+percent"
        )
        return dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(title),
                    dbc.CardBody(
                        dcc.Graph(
                            figure=figure,
                            config={
                                "displaylogo": False,
                            },
                        )
                    ),
                ]
            ),
            md=12,
            lg=6,
        )


class Metrics:
    """
    This class is used to manipulate all metrics registered.
    """

    def __init__(self, metrics: list):
        """
        Constructs the list of metric from the `metrics` list.

        :param metrics: List of metrics name.
        """
        self._metrics = Metrics._load_metrics(metrics)

        # Create output directory
        if not os.path.exists(Metric.OUTPUT_DIR):
            os.mkdir(Metric.OUTPUT_DIR)

    @staticmethod
    def _load_metrics(metrics) -> List[Metric]:
        """
        Load all metrics as plugins.
        By default, if no metrics is given, a default empty metric is loaded.

        :param metrics: List of metrics name to load.
        :return: Metrics classes loaded.
        """
        loaded_classes = []
        for metric in metrics:
            try:
                metric_module = importlib.import_module(f"metrics.{metric}")
                metric_class = None
                for obj in metric_module.__dict__.values():
                    if isinstance(obj, type) and Metric in obj.__bases__:
                        metric_class = obj
                        break
                if metric_class:
                    loaded_classes.append(metric_class())
                    logger.debug("Loaded metric class: %s", metric)
                else:
                    logger.error(
                        "No class inheriting from Metric found in metrics "
                        "module %s",
                        metric,
                    )
            except (ImportError, AttributeError) as e:
                logger.error("Error loading metric class %s: %s", metric, e)
        return loaded_classes

    def compute_dashboard(self, data: MetricData) -> List[dbc.Row]:
        """
        Compute widgets of the dashboard related to all metrics.

        :param data: Metric input data.
        :return: Dash widgets.
        """
        metrics_dashboard: list = []
        for metric in self._metrics:
            metrics_dashboard.extend(metric.compute_dashboard(data))
        return metrics_dashboard

    def compute_report(self, data: MetricData) -> List[MetricReport]:
        """
        Compute report related to all metrics.

        :param data: Metric input data.
        :return: Report of all metrics.
        """
        metrics_report: list = []
        for metric in self._metrics:
            metrics_report.append(metric.compute_report(data))
        return metrics_report
