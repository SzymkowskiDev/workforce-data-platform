"""
This script is the entry point of the dashboard. To launch it in the browser, run the following command:
    1. python wdp/employee_advisor/app.py
    2. The app will launch in your web browser at the address http://127.0.0.1:8050/
"""

from tabs.tab1_content import tab1_content
from tabs.tab2_content import tab2_content

from dash import Dash, html, Input, Output, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


# APP START
app = Dash(
    __name__,
    title="Employee Advisor",
    external_stylesheets=[dbc.themes.VAPOR, dbc.icons.BOOTSTRAP],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5",
        },
    ],
)


# TAB 1: Career Standing ##############################################################################

# Get user data


# User selection


# Visualise user personal data: avatar, name, email, phone, birthday, city


# City data


# Salary data


# Field-related info


# Skills data


# App callbacks go here
# @app.callback(Output("sankey-legit-location", "figure"), Input("sankey-input", "value"))


# TAB 2: EDA: IT Industry in 2023
# App callbacks go here e.g.
# BARCHART
# @app.callback(Output("class_barchart", "figure"), Input("intermediate-value", "data"))
# def update_bar_chart(data):
#     dff = pd.read_json(data, typ="series")
#     tn, fp, fn, tp = np.array(dff.get("Confusion Matrix")).ravel()
#     df = pd.DataFrame(
#         {
#             "Disaster": ["No", "Yes", "No", "Yes"],
#             "Actual": ["TRUE", "TRUE", "FALSE", "FALSE"],
#             "Count": [tn, tp, fn, fp],
#         }
#     )
#     fig = px.bar(
#         df,
#         x="Disaster",
#         y="Count",
#         color="Actual",
#         barmode="group",
#         text_auto=True,
#         color_discrete_sequence=["#48EF7B", "#D85360", "#48EF7B", "#D85360"],
#     )
#     fig.update_layout(
#         margin=dict(t=0, l=50),
#         height=350,
#         paper_bgcolor="rgba(0,0,0,0)",
#         plot_bgcolor="rgba(0,0,0,0)",
#         showlegend=False,
#         font=dict(size=14, color="#32FBE2"),
#     )

#     return fig


# TABS SETUP
tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Career Standing", tab_id="tab-1"),
        dbc.Tab(tab2_content, label="EDA: IT Market in 2023", tab_id="tab-2")
    ],
    active_tab="tab-1",
)

# LAYOUT
app.layout = dbc.Container(
    [html.H1([html.I(className="bi bi-chat-quote"),
             "  Empoloyee Advisor"]), tabs]
)

if __name__ == "__main__":
    app.run_server(debug=True)
