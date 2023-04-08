from dash import Dash, html, Input, Output, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# TAB 1: Career Standing
tab1_content = dbc.Card(
    dbc.CardBody(
        [
            # TOP PANEL: CAREER OVERVIEW
            dbc.Spinner(
                [
                    dbc.Row(
                        [
                            # html.H2("CAREER OVERVIEW", style={"marginTop": 25}),
                            # Column 1
                            dbc.Col(
                                [
                                    html.H3("Section 1",
                                            style={"fontSize": 20}),
                                    html.P(
                                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incidid"),
                                ],
                                width=4, xs=10, sm=8, md=5, lg=4, xl=4,
                            ),
                            # Column 2
                            dbc.Col(
                                [
                                    html.H3("Section 2",
                                            style={"fontSize": 20}),
                                    html.P(
                                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incidid"),
                                ],
                                width=4, xs=10, sm=8, md=5, lg=4, xl=4,
                            ),
                            # Column 3
                            dbc.Col(
                                [
                                    html.H3("Section 3", style={
                                            "fontSize": 20}),
                                    html.P(
                                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incidid"),
                                ],
                                width=4, xs=10, sm=8, md=5, lg=4, xl=4,
                            ),
                        ],
                    ),
                ],
                color="light",
                type="grow",
                spinner_style={"width": "15rem", "height": "15rem"}
            ),
            # BOTTOM PANEL - SKILLS
            dbc.Spinner(
                [
                    dbc.Row(
                        [
                            html.H2("SKILLS", style={"marginTop": 25}),
                            # Column 1
                            dbc.Col(
                                [
                                    html.H3("Specialization",
                                            style={"fontSize": 20}),
                                    html.P(
                                        "Based on your experience, your professional profile matches the following roles:"),

                                    dbc.Row([
                                        dbc.Col([html.Img(
                                            src="assets/avatars/developer.PNG", style={"width": "100%"})], width=4),
                                        dbc.Col([
                                            html.P("Developer (86%)", style={
                                                   "fontWeight": "bold"}),
                                            html.P("You know: Java, Django, Python, Apex, Flask")], width=8)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([html.Img(
                                            src="assets/avatars/technical_architect.PNG", style={"width": "100%"})], width=4),
                                        dbc.Col([
                                            html.P(
                                                "Technical Architect (32%)", style={"fontWeight": "bold"}),
                                            html.P("You know: AWS, Labda, EC2, Azure, DynamoDB")], width=8)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([html.Img(
                                            src="assets/avatars/database_administrator.PNG", style={"width": "100%"})], width=4),
                                        dbc.Col([
                                            html.P(
                                                "Database Administrator (62%)", style={"fontWeight": "bold"}),
                                            html.P("You know: SQL, Postgres, Redis, DynamoDB, Database Design")], width=8)
                                    ]),
                                ],
                                width=4, xs=10, sm=8, md=5, lg=4, xl=4,
                            ),
                            # Column 2
                            dbc.Col(
                                [
                                    html.H3("Recommendations",
                                            style={"fontSize": 20}),
                                    html.P(
                                        "Coworkers that share your skills also know the following: Jira, GitHub, Bitbucket, GitLab, Bitbucket Server, GitLab Server"),
                                    html.P(
                                        "Most in demand (highest paid) skills that relate to your career path are:"),
                                    html.P("BARCHART"),
                                    html.Img(
                                        src="assets/barchart.PNG", style={"width": "80%"})
                                ],
                                width=4, xs=10, sm=8, md=5, lg=4, xl=4,
                            ),
                            # Column 3
                            dbc.Col(
                                [
                                    html.H3("Section 3", style={
                                            "fontSize": 20}),
                                    html.P(
                                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incidid"),
                                ],
                                width=4, xs=10, sm=8, md=5, lg=4, xl=4,
                            ),
                        ], style={"backgroundColor": "#30115E"}
                    ),
                ],
                color="light",
                type="grow",
                spinner_style={"width": "15rem", "height": "15rem"}
            )
        ]
    ),
    className="mt-3",
)
