from dash import Dash, html, Input, Output, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# TAB 1: Career Standing
tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.H2("Introduction"),
        ]
    ),
    className="mt-3",
)
