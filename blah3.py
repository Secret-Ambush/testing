import dash
from dash import dcc, html, Input, Output
import pandas as pd
import os
import sqlalchemy
import snowflake.sqlalchemy
import snowflake.connector.pandas_tools

for k in ['HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(k, None)
    os.environ.pop(k.lower(), None)

engine = sqlalchemy.create_engine(
    os.environ['snowflake_conn'],
    execution_options=dict(autocommit=True)
)

app = dash.Dash(__name__)

 

app.layout = html.Div(
    children=[
        html.H1("Dropdown Demo"),
        html.Div(
            children=[
                html.Div(
                    dcc.Dropdown(
                        id="origin-dropdown",
                        placeholder="Select Origin",
                        multi=True  # Allow multiple selections
                    ),
                    style={"width": "200px", "display": "inline-block"}
                ),
                html.Div(
                    dcc.Dropdown(
                        id="dest-dropdown",
                        placeholder="Select Destination",
                        multi=True  # Allow multiple selections
                    ),
                    style={"width": "200px", "display": "inline-block"}
                ),
                html.Div(
                    dcc.Dropdown(
                        id="departure-date-dropdown",
                        placeholder="Select Departure Date",
                        multi=True  # Allow multiple selections
                    ),
                    style={"width": "200px", "display": "inline-block"}
                ),
                html.Div(
                    dcc.Dropdown(
                        id="flight-no",
                        placeholder="Select Flight number",
                        multi=True  # Allow multiple selections
                    ),
                    style={"width": "200px", "display": "inline-block"}
                ),
            ],
            style={"display": "flex", "justify-content": "space-between"}
        ),
        html.Div(id="output"),
    ]
)

 


snowflake_table = 'INVENTORY_SAMPLE_COPY'

 

@app.callback(
    Output("origin-dropdown", "options"),
    [Input("departure-date-dropdown", "value")]
)
def update_origin_options(selected_departure_dates):
    if selected_departure_dates:
        departure_dates_str = "', '".join(selected_departure_dates)
        origin_options_query = f"""
            SELECT DISTINCT LEG_ORIGIN
            FROM {snowflake_table}
            WHERE LEG_DEP_DATE IN ('{departure_dates_str}') ORDER BY LEG_ORIGIN
        """
    else:
        origin_options_query = f"""
            SELECT DISTINCT LEG_ORIGIN
            FROM {snowflake_table} ORDER BY LEG_ORIGIN
        """

 

    with engine.connect() as conn:
        origin_options = conn.execute(origin_options_query)
        return [{"label": row[0], "value": row[0]} for row in origin_options]


@app.callback(
    Output("dest-dropdown", "options"),
    [Input("origin-dropdown", "value")]
)
def update_destinations(selected_origins):
    if selected_origins:
        origins_str = "', '".join(selected_origins)
        query = f"""
            SELECT DISTINCT LEG_DESTINATION
            FROM {snowflake_table}
            WHERE LEG_ORIGIN IN ('{origins_str}') ORDER BY LEG_DESTINATION
        """
        with engine.connect() as conn:
            result = conn.execute(query)
            destinations = [row[0] for row in result]
            return [{"label": dest, "value": dest} for dest in destinations]
    return []

 


@app.callback(
    Output("departure-date-dropdown", "options"),
    [Input("origin-dropdown", "value"),
     Input("dest-dropdown", "value")]
)
def update_departure_dates(selected_origins, selected_destinations):
    if selected_origins and selected_destinations:
        origins_str = "', '".join(selected_origins)
        destinations_str = "', '".join(selected_destinations)
        departure_date_options_query = f"""
            SELECT DISTINCT LEG_DEP_DATE
            FROM {snowflake_table}
            WHERE LEG_ORIGIN IN ('{origins_str}')
            AND LEG_DESTINATION IN ('{destinations_str}') ORDER BY LEG_DEP_DATE
        """

 

    with engine.connect() as conn:
        departure_date_options = conn.execute(departure_date_options_query)
        return [{"label": row[0], "value": row[0]} for row in departure_date_options]

@app.callback(
    Output("flight-no", "options"),
    [Input("origin-dropdown", "value"),
     Input("dest-dropdown", "value"),
     Input("departure-date-dropdown", "value")]
)
def update_flight_numbers(selected_origins, selected_destinations, selected_departure_dates):
    if selected_origins and selected_destinations and selected_departure_dates:
        origins_str = "', '".join(selected_origins)
        destinations_str = "', '".join(selected_destinations)
        departure_dates_str = "', '".join(selected_departure_dates)
        flight_number_options_query = f"""
            SELECT DISTINCT FLTNUM
            FROM {snowflake_table}
            WHERE LEG_ORIGIN IN ('{origins_str}')
            AND LEG_DESTINATION IN ('{destinations_str}')
            AND LEG_DEP_DATE IN ('{departure_dates_str}') ORDER BY FLTNUM
        """

 

    with engine.connect() as conn:
        flight_number_options = conn.execute(flight_number_options_query)
        return [{"label": row[0], "value": row[0]} for row in flight_number_options]

if __name__ == "__main__":
    app.run_server()