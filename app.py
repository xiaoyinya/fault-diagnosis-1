# Packages
import pandas as pd

# Plotly
import plotly.graph_objects as go

# Dash
import dash
# import dash_core_components as dcc
from dash import dcc

import dash.dependencies as dd
# import dash_html_components as html
from dash import html

# Import data
train = pd.read_csv("train/01_M01_DC_train.csv")
train_ttf = pd.read_csv("train/train_ttf/01_M01_DC_train.csv")
train_faults = pd.read_csv("train/train_faults/01_M01_train_fault_data.csv")

# Merge data
df = train.merge(train_faults, how='outer', on=['time', 'Tool'], left_on=None, right_on=None, left_index=False,
                    right_index=False, sort=False, copy=True, indicator=False, validate=None)
df = df.sort_values(by='time', ascending=True)

# Variables
variables = df.columns[7:23].tolist()

# App ------------------------------------------------------------------------------------------------------------------
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div(children=[
    # Title
    html.H1(children='Time Series Plots of Features'),

    # Dropdown menu
    dcc.Dropdown(
        id='feature',
        options=[{'label': name, 'value': name} for name in variables],
        value=variables[0],
    ),

    # Graph
    dcc.Graph(
        id='time-series'
    )
])

# End of App Code ------------------------------------------------------------------------------------------------------

# Callback function -- this make it dynamic
@app.callback(
    dd.Output('time-series', 'figure'),
    [dd.Input('feature', 'value')]
)

def time_series(variable):

    # Time bounds for data
    lower_bound = 40082846
    upper_bound = 40567036

    # Get subset
    train_n = df[df['time'].between(lower_bound, upper_bound, inclusive=True)]
    fault_n = train_faults[train_faults['time'].between(lower_bound, upper_bound, inclusive=True)]

    # Initialize
    fig = go.Figure()

    # Main Graph
    fig.add_trace(go.Scatter(x=list(train_n['time']), y=list(train_n[variable])))

    # Add fault lines
    fault_records = len(fault_n)

    # Min and Max for Vertical Lines
    minimum = min(train_n[variable])
    maximum = max(train_n[variable])

    for index in range(0, fault_records):
        # Get fault type for instance
        fault_type = fault_n.iloc[index, 1]

        # Get matching time
        time = fault_n.iloc[index, 0]

        # Line color depending on fault type
        if fault_type == "FlowCool Pressure Dropped Below Limit":
            line_color = "red"
        elif fault_type == "Flowcool Pressure Too High Check Flowcool Pump":
            line_color = "green"
        elif fault_type == "Flowcool leak":
            line_color = "DarkOrange"

        # Code vertical line for fault
        fig.add_shape(type="line", x0=time, y0=minimum, x1=time, y1=maximum, line=dict(color=line_color, width=2))

    # Range slider
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="linear"))

    return fig

# Run App
if __name__ == '__main__':
    app.run_server(debug=True)
