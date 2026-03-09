import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import plotly.express as px

API_URL = "https://pali-analytics-api-1.onrender.com/competitors"

app = dash.Dash(__name__)
server = app.server


def metric_card(title, value):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "14px", "color": "#888"}),
            html.Div(value, style={"fontSize": "28px", "fontWeight": "bold"}),
        ],
        style={
            "border": "1px solid #eee",
            "padding": "20px",
            "borderRadius": "10px",
            "width": "200px",
            "textAlign": "center",
            "boxShadow": "0px 2px 6px rgba(0,0,0,0.05)",
        },
    )


app.layout = html.Div(
    [
        html.H1("Pali Analytics – Market Intelligence"),

        html.Div(
            [
                dcc.Input(id="business_name", placeholder="Business Name", debounce=True),
                dcc.Input(id="address", placeholder="Business Address", debounce=True),
                html.Button("Run Analysis", id="run_button", n_clicks=0),
            ],
            style={"marginBottom": "30px"},
        ),

        html.Div(id="market_cards", style={"display": "flex", "gap": "20px", "marginBottom": "30px"}),

        html.Div(id="competitor_cards", style={"display": "flex", "gap": "20px", "marginBottom": "40px"}),

        dcc.Graph(id="competitor_chart"),

        html.H3("1 Mile Competitors"),
        dash_table.DataTable(id="table_1"),

        html.H3("3 Mile Competitors"),
        dash_table.DataTable(id="table_3"),

        html.H3("5 Mile Competitors"),
        dash_table.DataTable(id="table_5"),
    ]
)


@app.callback(
    [
        Output("market_cards", "children"),
        Output("competitor_cards", "children"),
        Output("competitor_chart", "figure"),
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
)
def update_dashboard(n_clicks, business_name, address):

    if not n_clicks or not business_name or not address:
        return [], [], {}, [], [], [], [], [], []

    try:
        params = {"business_name": business_name, "address": address}
        response = requests.get(API_URL, params=params, timeout=30).json()

        print("API response:", response)

        # Extract data safely
        client = response.get("client", {})
        market = response.get("market_data") or {}

        df1 = pd.DataFrame(response.get("radius_1_mile", []))
        df3 = pd.DataFrame(response.get("radius_3_mile", []))
        df5 = pd.DataFrame(response.get("radius_5_mile", []))

        # MARKET CARDS
        market_cards = [
            metric_card("Population", market.get("population", "-")),
            metric_card("Median Income", market.get("median_income", "-")),
            metric_card("Median Age", market.get("median_age", "-")),
        ]

        # COMPETITOR CARDS
        competitor_cards = [
            metric_card("Competitors (1 Mile)", len(df1)),
            metric_card("Competitors (3 Mile)", len(df3)),
            metric_card("Competitors (5 Mile)", len(df5)),
            metric_card("Client Rating", client.get("rating") or "-"),
            metric_card("Client Reviews", client.get("reviews") or "-"),
        ]

        # BUILD CHART
        frames = [df for df in [df1, df3, df5] if not df.empty]

        if frames:
            combined = pd.concat(frames, ignore_index=True)

            # Clean nulls for Plotly
            combined = combined.dropna(subset=["rating", "reviews"])

            if not combined.empty:
                fig = px.scatter(
                    combined,
                    x="reviews",
                    y="rating",
                    hover_name="name",
                    title="Competitor Rating vs Review Volume",
                )
            else:
                fig = px.scatter(title="No competitor data available")
        else:
            fig = px.scatter(title="No competitor data available")

        # TABLE BUILDER
        def build_table(df):
            if df.empty:
                return [], []
            return df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]

        data1, cols1 = build_table(df1)
        data3, cols3 = build_table(df3)
        data5, cols5 = build_table(df5)

        return (
            market_cards,
            competitor_cards,
            fig,
            data1,
            cols1,
            data3,
            cols3,
            data5,
            cols5,
        )

    except Exception as e:
        print("Dashboard error:", e)
        return [], [], {}, [], [], [], [], [], []


if __name__ == "__main__":
    app.run_server()
