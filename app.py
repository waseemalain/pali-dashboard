import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import requests
import pandas as pd

API_URL = "https://pali-analytics-api-1.onrender.com/competitors"

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Pali Analytics – Competitor Dashboard"),

    html.Div([
        dcc.Input(id="business_name", placeholder="Business Name", style={"marginRight": "10px"}),
        dcc.Input(id="address", placeholder="Business Address", style={"marginRight": "10px"}),
        dcc.Input(id="category", placeholder="Category (e.g. pizza)", style={"marginRight": "10px"}),
        html.Button("Run Analysis", id="run_button", n_clicks=0)
    ], style={"marginBottom": "20px"}),

    html.Div(id="summary_output"),

    html.H3("1 Mile Competitors"),
    dash_table.DataTable(id="table_1"),

    html.H3("3 Mile Competitors"),
    dash_table.DataTable(id="table_3"),

    html.H3("5 Mile Competitors"),
    dash_table.DataTable(id="table_5"),
])


@app.callback(
    [
        Output("summary_output", "children"),
        Output("table_1", "data"),
        Output("table_1", "columns"),
        Output("table_3", "data"),
        Output("table_3", "columns"),
        Output("table_5", "data"),
        Output("table_5", "columns"),
    ],
    Input("run_button", "n_clicks"),
    State("business_name", "value"),
    State("address", "value"),
    State("category", "value"),
)
def update_dashboard(n_clicks, business_name, address, category):

    if n_clicks == 0:
        return "", [], [], [], [], [], []

    params = {
        "business_name": business_name,
        "address": address,
        "category": category
    }

    response = requests.get(API_URL, params=params).json()

    df1 = pd.DataFrame(response.get("radius_1_mile", []))
    df3 = pd.DataFrame(response.get("radius_3_mile", []))
    df5 = pd.DataFrame(response.get("radius_5_mile", []))

    summary = html.Div([
        html.H2("Competitive Summary"),
        html.P(f"1 Mile Competitors: {len(df1)}"),
        html.P(f"3 Mile Competitors: {len(df3)}"),
        html.P(f"5 Mile Competitors: {len(df5)}"),
    ])

    def build_table(df):
        if df.empty:
            return [], []
        return df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]

    data1, cols1 = build_table(df1)
    data3, cols3 = build_table(df3)
    data5, cols5 = build_table(df5)

    return summary, data1, cols1, data3, cols3, data5, cols5


if __name__ == "__main__":
    app.run_server(debug=False)
