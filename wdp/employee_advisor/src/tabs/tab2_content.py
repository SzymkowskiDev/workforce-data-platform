# IMPORT LOCAL
from dashboard.src.models.production.generate_perf_report import generate_perf_report
from dashboard.src.models.production.vectorize_data import vectorize_data
from dashboard.src.models.production.preprocess_data import preprocess_data

# IMPORT EXTERNAL
import time
from dash import Dash, html, Input, Output, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import auc
import plotly.figure_factory as ff
from wordcloud import WordCloud, STOPWORDS
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import io
import requests
from bs4 import BeautifulSoup
import re
import nltk
import seaborn as sns
import string
import json
import string
import emoji
import itertools
from collections import Counter
from scipy.stats import kstest


svg = """
<svg
  height="70"
  width="100"
  viewBox="0 0 100% 100%"
  xmlns="http://www.w3.org/2000/svg"
>
  <rect width="100%" height="100%">
    <animate
      attributeName="rx"
      values="0;50;0"
      dur="5s"
      repeatCount="indefinite"
    />
  </rect>
  <circle r="40%" cx="50%" cy="50%" fill="#ffffff"></circle>
  <circle r="20%" cx="50%" cy="50%" fill="#000000">
    <animate
      attributeName="r"
      values="20%;40%;20%"
      dur="5s"
      repeatCount="indefinite"
    />
  </circle>
</svg>
"""


# REUSABLE COMPONENTS
progress = html.Div(
    [
        dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
        dbc.Progress(id="progress", striped=True, color="success"),
    ]
)

# TAB 2: CLASSIFICATION ##############################################################################################################
tab2_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    html.H2("INPUTS"),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("Data Cleaning", style={
                                        "fontSize": 20}),
                                    dbc.Checklist(
                                        options=[
                                            {"label": "Remove hashes", "value": 1},
                                            {
                                                "label": "Remove HTML special entities",
                                                "value": 2,
                                            },
                                            {"label": "Remove tickers", "value": 3},
                                            {"label": "Remove hyperlinks",
                                             "value": 4},
                                            {"label": "Remove whitespaces",
                                             "value": 5},
                                            {
                                                "label": "Remove URL, RT, mention(@)",
                                                "value": 6,
                                            },
                                            {
                                                "label": "Remove no BMP characters",
                                                "value": 7,
                                            },
                                            {
                                                "label": "Remove misspelled words",
                                                "value": 8,
                                            },
                                            {"label": "Remove emojis", "value": 9},
                                            {"label": "Remove Mojibake",
                                             "value": 10},
                                            {
                                                "label": "Tokenize & Lemmatize",
                                                "value": 11,
                                            },
                                            {"label": "Leave only nouns",
                                             "value": 12},
                                            {
                                                "label": "Spell check",
                                                "value": 13,
                                                "disabled": True,
                                            },
                                        ],
                                        id="preprocessing-checklist",
                                    ),
                                ]
                            )
                        ],
                        width=4, xs=10, sm=8, md=5, lg=4, xl=4, style={"marginTop": 25, "marginBottom": 25}
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("Vectorization", style={
                                        "fontSize": 20}),
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "Count", "value": "count"},
                                            {"label": "TF-IDF", "value": "tfidf"},
                                            {
                                                "label": "Word2Vec ",
                                                "value": "W2V",
                                                "disabled": True,
                                            }
                                            # TODO: implement this
                                        ],
                                        value="tfidf",
                                        id="vectorization-radio-items",
                                    ),
                                ]
                            )
                        ],
                        width=4, xs=10, sm=8, md=5, lg=4, xl=4, style={"marginTop": 25}
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("Model", style={"fontSize": 20}),
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "SVC", "value": "SVC"},
                                            {"label": "Logistic",
                                             "value": "Logistic"},
                                            {"label": "Naive Bayes",
                                             "value": "Bayes"},
                                            {
                                                "label": "LSTM ANN model",
                                                "value": "LSTM",
                                                "disabled": True,
                                            },
                                            {
                                                "label": "BERT model",
                                                "value": "BERT",
                                                "disabled": True,
                                            },
                                            {
                                                "label": "roBERTa model",
                                                "value": "roBERTa",
                                                "disabled": True,
                                            },
                                            # TODO: add other models
                                        ],
                                        value="Logistic",
                                        id="model-radio-items",
                                    ),
                                ]
                            )
                        ],
                        width=4, xs=10, sm=8, md=5, lg=4, xl=4, style={"marginTop": 25}
                    )
                ],
            ),
            dbc.Spinner(
                [
                    dbc.Row(
                        [
                            # H1 Raport
                            html.H2("REPORT", style={"marginTop": 25}),
                            # First column & Confusion Matrix
                            dbc.Col(
                                [
                                    html.Div(
                                        id="performance-metrics-accuracy-text"),
                                    html.H3(
                                        "Fig 1. Confusion Matrix data", style={"fontSize": 20}
                                    ),
                                    dcc.Graph(id="class_barchart"),
                                ],
                                width=4, xs=10, sm=8, md=5, lg=4, xl=4,
                            ),

                            # Second column & Performance Metrics
                            dbc.Col(
                                [
                                    html.Div(
                                        id="performance-metrics-precison-text"),
                                    html.H3(
                                        "Fig 2. Performance Metrics", style={"fontSize": 20}
                                    ),
                                    html.Div(
                                        [
                                            html.Div(id="output-datatable"),
                                            dcc.Store(id="intermediate-value"),
                                        ]
                                    ),
                                    html.P(id="performance-metrics-recall-text")
                                ],
                                width=4, xs=10, sm=8, md=5, lg=4, xl=4,
                            ),

                            # Third column & ROC & AUC
                            dbc.Col(
                                [
                                    html.P(
                                        "Fig 3. shows the performance of the classification model at all classification thresholds."
                                    ),
                                    html.H3("Fig 3. ROC & AUC",
                                            style={"fontSize": 20}),
                                    dcc.Graph(id="roc-graph"),
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
