#! python3

"""
Status chart.
"""
import logging
from typing import List

import dash_bootstrap_components as dbc
import plotly.express as px

from .metric import Metric, MetricData, MetricReport

#: Create logger for this file.
logger = logging.getLogger()


class Status(Metric):
    """
    This class is used to provide metric about status.
    """

    def compute_dashboard(self, data: MetricData) -> List[dbc.Row]:
        """
        Interface to compute widget of the dashboard related to this metric.

        :param data: Metric input data.
        :return: Dash widgets.
        """
        figure_list = []
        for issue_type, figure in self.status_per_issue_type(data).items():
            figure_list.append(
                self._draw_figure(f"Status per {issue_type}", figure)
            )
        return [dbc.Row(figure_list, class_name="row g-2")]

    def compute_report(self, data: MetricData) -> MetricReport:
        """
        Interface to compute widget of the report related to this metric.

        :param data: Metric input data.
        :return: Report of the metric.
        """
        figures = []
        issue_types = []
        for issue_type, figure in self.status_per_issue_type(data).items():
            figure_path = f"{self.OUTPUT_DIR}/{issue_type}.png"
            figure.write_image(figure_path)
            figures.append(figure_path)
            issue_types.append(issue_type)
        return MetricReport(
            metric_name="Status",
            figures=figures,
            report_data={"issue_types": issue_types},
        )

    @staticmethod
    def status_per_issue_type(data: MetricData) -> dict:
        """
        Compute the number of tickets in a status for each issue type.

        :param data: Metric input data.
        :return: Dictionary with a graph for each issue type name.
        """
        result = {}

        groups = data.changes.merge(data.info, on="key").groupby("type")

        for issue_type, group in groups:
            df_per_type = group[["key", "status"]].drop_duplicates(
                subset="key", keep="last"
            )
            status_per_type = (
                df_per_type["status"]
                .cat.remove_unused_categories()
                .value_counts(sort=False)
            )

            result[issue_type] = px.pie(
                values=status_per_type, names=status_per_type.index, hole=0.4
            )

        return result
