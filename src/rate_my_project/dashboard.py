#! python3

"""
Web dashboard to explore metrics.
"""

import asyncio

from dash import dcc, Dash, DiskcacheManager, html, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import diskcache

# from werkzeug.middleware.profiler import ProfilerMiddleware

from .config import GlobalConfig
from .metrics import Metric, MetricData
from .utils import fetch_tickets_information

# local cache to store query results
cache = diskcache.FanoutCache()
# Jira client to do the requests
CONFIG: GlobalConfig


def create_application_layout() -> html.Div:
    """
    Create layout of dashboard application dashboard.
    """
    navbar = dbc.NavbarSimple(
        children=[],
        brand="Rate My Project",
        brand_href="#",
        color="primary",
        dark=True,
        className="mb-3",
    )

    search = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Input(
                                id="jql_input",
                                type="text",
                                placeholder="Enter your JQL query here",
                            ),
                            dbc.FormFeedback(
                                "Valid JQL query",
                                id="jql_ok",
                                type="valid",
                            ),
                            dbc.FormFeedback(
                                "", id="jql_error", type="invalid"
                            ),
                        ]
                    ),
                    dbc.Col(
                        dbc.Button("Run Analysis", id="run_button"),
                        width="auto",
                    ),
                ],
            ),
        ],
        className="mb-3",
    )

    return html.Div(
        [
            # List of tickets retrieved with last JQL query.
            dcc.Store(id="tickets", storage_type="session"),
            navbar,
            search,
            dbc.Container(id="metrics"),
        ],
    )


def create_application() -> Dash:
    """
    Create dashboard application and define the layout of the dashboard.
    """
    app = Dash(
        external_stylesheets=[dbc.themes.COSMO],
        background_callback_manager=DiskcacheManager(cache, expire=60),
    )
    load_figure_template("cosmo")
    app.layout = create_application_layout()
    return app


application = create_application()


@cache.memoize(typed=True, expire=60)
def fetch_data_for_metric_from_jql(jql: str) -> MetricData:
    """
    Fetch the tickets from `JQL` query and create data used by metric.
    The data is cached during 60s to avoid too many requests to the server.

    :param jql: JQL query.
    :return: Data for metric.
    """
    jira_information = asyncio.run(
        fetch_tickets_information(CONFIG.jira_client(), jql)
    )
    return MetricData.from_tickets_and_changelogs(
        CONFIG.config.fields.dict(),
        CONFIG.config.projects[0].workflow_to_dict(),
        *jira_information,
    )


@application.callback(
    inputs=Input("jql_input", "n_submit"),
    state=State("run_button", "n_clicks"),
    output=Output("run_button", "n_clicks"),
)
def on_jql_input_entered(jql, run_button_clicks):
    """
    When the JQL is validated with enter, it runs the analysis by simulating a
    click on the run button.
    """
    if not jql:
        raise PreventUpdate

    if run_button_clicks:
        return run_button_clicks + 1
    return 1


@application.callback(
    inputs=Input("run_button", "n_clicks"),
    state=State("jql_input", "value"),
    output=Output("metrics", "children"),
    background=True,
    running=[
        (Output("run_button", "disabled"), True, False),
    ],
)
def on_run_button_clicked(_, jql):
    """
    Execute the analysis when the run button is clicked by fetching the tickets
    from JQL query.
    """
    if not jql:
        raise PreventUpdate
    tickets = fetch_data_for_metric_from_jql(jql)
    metrics_dashboard: list = []
    for metric in Metric.metrics_list:
        metrics_dashboard.extend(metric().compute_dashboard(tickets))
    return metrics_dashboard


@application.callback(
    inputs=Input("jql_input", "value"),
    output=[
        Output("jql_input", "valid"),
        Output("jql_input", "invalid"),
        Output("jql_error", "children"),
    ],
)
def on_jql_input_updated(jql):
    """
    Validate the JQL query syntax.
    """
    if not jql:
        return False, False, ""
    try:
        asyncio.run(CONFIG.jira_client().validate_jql(jql))
        return True, False, ""
    except Exception as error:
        return False, True, str(error)


def start_web_application(global_config: GlobalConfig) -> None:
    """
    Start dashboard server.
    """
    global CONFIG
    CONFIG = global_config
    # Profiling
    # application.server.config["PROFILE"] = True
    # application.server.wsgi_app = ProfilerMiddleware(
    #     application.server.wsgi_app, sort_by=("cumtime", "tottime"),
    #     restrictions=[50]
    # )
    application.run_server(debug=False)
