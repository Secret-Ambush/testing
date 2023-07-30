import dash
from dash import dcc, html, Input, Output
import os
import sqlalchemy

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
                        dcc.Dropdown(
                            id="origin-dropdown",
                            placeholder="Select Origin",
                        ),
                        dcc.Dropdown(
                            id="departure-date-dropdown",
                            placeholder="Select Departure Date",
                        ),
                        dcc.Dropdown(
                            id="leg-destination-dropdown",
                            placeholder="Select destination",
                        ),
                        dcc.Dropdown(
                            id="flt-no-dropdown",
                            placeholder="Select flight number",
                        ),
                        html.Div(id="output"),
                    ],
                    style={"display": "flex", "justify-content": "space-between"}
                ),
                html.Div(id="output"),
            ]
        )

@app.callback(
    Output("origin-dropdown", "options"),
    Output("origin-dropdown", "value"),
    Output("departure-date-dropdown", "options"),
    Output("leg-destination-dropdown", "options"),
    Output("flt-no-dropdown", "options"),
    [Input("origin-dropdown", "value")]
)
def update_dropdowns(selected_origin):
    origin_options_query = """
        SELECT DISTINCT LEG_ORIGIN
        FROM inventory_sample_copy
    """

    if selected_origin:
        departure_date_options_query = f"""
            SELECT DISTINCT LEG_DEP_DATE
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin}'
        """
        leg_destination_options_query = f"""
            SELECT DISTINCT LEG_DESTINATION
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin}'
        """
        flt_no_options_query = f"""
            SELECT DISTINCT FLTNUM
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin}'
        """
    else:
        departure_date_options_query = ""
        leg_destination_options_query = ""
        flt_no_options_query = ""

    with engine.connect() as conn:
        origin_options = conn.execute(origin_options_query)
        origin_options = [{"label": row[0], "value": row[0]} for row in origin_options]

        departure_date_options = conn.execute(departure_date_options_query)
        departure_date_options = [{"label": row[0], "value": row[0]} for row in departure_date_options]

        leg_destination_options = conn.execute(leg_destination_options_query)
        leg_destination_options = [{"label": row[0], "value": row[0]} for row in leg_destination_options]

        flt_no_options = conn.execute(flt_no_options_query)
        flt_no_options = [{"label": row[0], "value": row[0]} for row in flt_no_options]

        return origin_options, selected_origin, departure_date_options, leg_destination_options, flt_no_options

if __name__ == "__main__":
    app.run_server(debug=True)
