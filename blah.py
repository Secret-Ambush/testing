import dash
from dash import dcc, html, Input, Output
import pandas as pd
import os
import sqlalchemy
import snowflake.sqlalchemy
import snowflake.connector.pandas_tools


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
        html.H1("Dropdown Demo"),
        html.Div(
            children=[
                html.Div(
                        dcc.Dropdown(
                            id="origin-dropdown",
                            placeholder="Select Origin",
                        ),
                        style={"width": "200px", "display": "inline-block"}
                ),
                html.Div(
                        dcc.Dropdown(
                            id="departure-date-dropdown",
                            placeholder="Select Departure Date",
                        ),
                        style={"width": "200px", "display": "inline-block"}
                ),
                html.Div(
                        dcc.Dropdown(
                            id="leg-destination-dropdown",
                            placeholder="Select destination",
                        ),
                        style={"width": "200px", "display": "inline-block"}
                ),
                html.Div(
                        dcc.Dropdown(
                            id="flt-no-dropdown",
                            placeholder="Select flight number",
                        ),
                        style={"width": "200px", "display": "inline-block"}
                ),    
                    ],
                    style={"display": "flex", "justify-content": "space-between"}
                ),
                html.Div(id="output"),
            ]
        )

@app.callback(
    dash.dependencies.Output("origin-dropdown", "options"),
    [dash.dependencies.Input("departure-date-dropdown", "value")],
)
def update_origin_options(selected_departure_date):
    if selected_departure_date:
        origin_options_query = f"""
            SELECT DISTINCT LEG_ORIGIN
            FROM inventory_sample_copy
            WHERE LEG_DEP_DATE = '{selected_departure_date} ORDER BY LEG_ORIGIN ASC'
        """
    else:
        origin_options_query = """
            SELECT DISTINCT LEG_ORIGIN
            FROM inventory_sample_copy
            ORDER BY LEG_ORIGIN ASC
        """

    with engine.connect() as conn:
        origin_options = conn.execute(origin_options_query)
        return [{"label": row[0], "value": row[0]} for row in origin_options]


@app.callback(
    dash.dependencies.Output("departure-date-dropdown", "options"),
    dash.dependencies.Output("leg-destination-dropdown", "options"),
    dash.dependencies.Output("flt-no-dropdown", "options"),
    [dash.dependencies.Input("origin-dropdown", "value")],
)
def update_based_on_origin(selected_origin):
    if selected_origin:
        departure_date_options_query = f"""
            SELECT DISTINCT LEG_DEP_DATE
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin}'
            ORDER BY LEG_DEP_DATE ASC
        """
        leg_destination_options_query = f"""
            SELECT DISTINCT LEG_DESTINATION
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin}' 
            ORDER BY LEG_DESTINATION ASC
        """
        flt_no_options_query = f"""
            SELECT DISTINCT FLTNUM
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin}'
            ORDER BY FLTNUM ASC
        """
    else:
        departure_date_options_query = """
            SELECT DISTINCT LEG_DEP_DATE
            FROM inventory_sample_copy
            ORDER BY LEG_DEP_DATE ASC
        """
        leg_destination_options_query = """
            SELECT DISTINCT LEG_DESTINATION
            FROM inventory_sample_copy
            ORDER BY LEG_DESTINATION ASC
        """
        flt_no_options_query = """
            SELECT DISTINCT FLTNUM
            FROM inventory_sample_copy
            ORDER BY FLTNUM ASC
        """

    with engine.connect() as conn:
        departure_date_options = conn.execute(departure_date_options_query)
        dept_date_opt = [{"label": row[0], "value": row[0]} for row in departure_date_options]

        leg_destination_options = conn.execute(leg_destination_options_query)
        leg_dest_opt = [{"label": row[0], "value": row[0]} for row in leg_destination_options]
    
        flt_no_options = conn.execute(flt_no_options_query)
        flt_no_opt = [{"label": row[0], "value": row[0]} for row in flt_no_options]

        return dept_date_opt, leg_dest_opt, flt_no_opt

@app.callback(
    dash.dependencies.Output("departure-date-dropdown", "options"),
    dash.dependencies.Output("flt-no-dropdown", "options"),
    [dash.dependencies.Input("leg-destination-dropdown", "value")],
    [dash.dependencies.Input("origin-dropdown", "value")],
)
def update_based_on_origin_and_dest(selected_origin,selected_dest):
    if selected_origin & selected_dest:
        departure_date_options_query2 = f"""
            SELECT DISTINCT LEG_DEP_DATE
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin} AND
            LEG_DESTINATION = '{selected_dest}'
        """
        flt_no_options_query2 = f"""
            SELECT DISTINCT FLTNUM
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin}' AND
            LEG_DESTINATION = '{selected_dest}'
        """
    else:
        departure_date_options_query2 = """
            SELECT DISTINCT LEG_DEP_DATE
            FROM inventory_sample_copy
        """
        flt_no_options_query2 = """
            SELECT DISTINCT FLTNUM
            FROM inventory_sample_copy
        """

    with engine.connect() as conn:
        departure_date_options = conn.execute(departure_date_options_query2)
        dept_date_opt2 = [{"label": row[0], "value": row[0]} for row in departure_date_options]
    
        flt_no_options = conn.execute(flt_no_options_query2)
        flt_no_opt2 = [{"label": row[0], "value": row[0]} for row in flt_no_options]

        return dept_date_opt2, flt_no_opt2

@app.callback(
    dash.dependencies.Output("flt-no-dropdown", "options"),
    [dash.dependencies.Input("departure-date-dropdown", "options")],
    [dash.dependencies.Input("leg-destination-dropdown", "value")],
    [dash.dependencies.Input("origin-dropdown", "value")],
)
def update_based_on_origin_and_dest_and_deptdate(selected_origin,selected_dest, selected_dept_date):
    if selected_origin & selected_dest & selected_dept_date:
        flt_no_options_query3 = f"""
            SELECT DISTINCT FLTNUM
            FROM inventory_sample_copy
            WHERE LEG_ORIGIN = '{selected_origin}' AND
            LEG_DESTINATION = '{selected_dest}' AND
            SEG_DEPT_DATE = '{selected_dept_date}'
        """
    else:
        flt_no_options_query3 = """
            SELECT DISTINCT FLTNUM
            FROM inventory_sample_copy
        """

    with engine.connect() as conn:
        flt_no_options = conn.execute(flt_no_options_query3)
        flt_no_opt3 = [{"label": row[0], "value": row[0]} for row in flt_no_options]

        return flt_no_opt3

if __name__ == "__main__":
    app.run_server(debug=True)