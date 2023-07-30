import dash
from dash import dcc, html, Input, Output
import pandas as pd
import os
import sqlalchemy

# execute to ensure local proxy variables not used
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
        html.H1("Dropdown App"),
        html.Label("Leg Origin:"),
        dcc.Dropdown(
            id="leg-origin-dropdown",
            placeholder="Select Origin",
        ),
        html.Label("Leg Destination:"),
        dcc.Dropdown(
            id="leg-destination-dropdown",
            placeholder="Select Destination",
        ),
        html.Label("Segment Departure Date:"),
        dcc.Dropdown(
            id="seg-dept-date-dropdown",
            placeholder="Select Departure Date",
        ),
        html.Label("Flight Number:"),
        dcc.Dropdown(
            id="flt-no-dropdown",
            placeholder="Select Flight Number",
        ),
        html.Div(id="output")
    ]
)


@app.callback(
    Output("leg-origin-dropdown", "options"),
    [Input("leg-origin-dropdown", "value")]
)
def populate_leg_origin_dropdown(leg_origin):
    leg_origin_query = "SELECT DISTINCT LEG_ORIGIN FROM INVENTORY_SAMPLE_COPY"
    with engine.connect() as connection:
        leg_origin_df = pd.read_sql_query(leg_origin_query, connection)
        leg_origin_options = [{'label': row['LEG_ORIGIN'], 'value': row['LEG_ORIGIN']} for _, row in leg_origin_df.iterrows()]
    return leg_origin_options


@app.callback(
    Output("leg-destination-dropdown", "options"),
    Output("seg-dept-date-dropdown", "options"),
    Output("flt-no-dropdown", "options"),
    [Input("leg-origin-dropdown", "value")]
)
def update_dropdowns(leg_origin):
    leg_dest_query = f"SELECT DISTINCT LEG_DESTINATION FROM INVENTORY_SAMPLE_COPY WHERE LEG_ORIGIN = '{leg_origin}'"
    seg_dept_date_query = "SELECT DISTINCT SEG_DEP_DATE FROM INVENTORY_SAMPLE_COPY"
    flt_no_query = "SELECT DISTINCT FLTNUM FROM INVENTORY_SAMPLE_COPY"

    with engine.connect() as connection:
        leg_dest_df = pd.read_sql_query(leg_dest_query, connection)
        leg_dest_options = [{'label': row['LEG_DESTINATION'], 'value': row['LEG_DESTINATION']} for _, row in leg_dest_df.iterrows()]

        seg_dept_date_df = pd.read_sql_query(seg_dept_date_query, connection)
        dept_date_options = [{'label': row['SEG_DEP_DATE'].strftime('%Y-%m-%d'), 'value': row['SEG_DEP_DATE'].strftime('%Y-%m-%d')} for _, row in seg_dept_date_df.iterrows()]

        flt_no_df = pd.read_sql_query(flt_no_query, connection)
        flt_no_options = [{'label': row['FLTNUM'], 'value': row['FLTNUM']} for _, row in flt_no_df.iterrows()]

    return leg_dest_options, dept_date_options, flt_no_options


if __name__ == '__main__':
    app.run_server(debug=True)
