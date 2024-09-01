import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from neuralprophet import NeuralProphet
import json
from transformers import pipeline
import base64
import torch
import os
from llama_cpp import Llama

# Load and process the expanded data
with open('warehouse_inventory.json') as f:
    warehouse_data = json.load(f)

# Extracting inventory data
inventory_df = pd.DataFrame(warehouse_data['warehouse']['inventory'])

# Process sales data correctly
sales_data_dict = warehouse_data['warehouse']['sales_data']
sales_data = pd.DataFrame([(k, month, item, sales) for k, v in sales_data_dict.items()
                           for month, data in v.items() for item, sales in data.items()],
                          columns=['Year', 'Month', 'Material', 'Sales'])

sales_data['YearMonth'] = pd.to_datetime(sales_data['Year'] + '-' + sales_data['Month'], format='%Y-%B')
sales_data = sales_data.sort_values(by='YearMonth')

# Process nearby inventories/plants and shippers data
nearby_inventories = []
for nearby in warehouse_data['warehouse']['nearby_inventories']:
    if 'inventory' in nearby:
        for material, quantity in nearby['inventory'].items():
            nearby_inventories.append({
                'name': nearby['name'],
                'location': nearby['location'],
                'material': material,
                'quantity': quantity,
                'distance_km': nearby['distance_km']
            })
    elif 'production_capacity_per_month' in nearby:
        for material, capacity in nearby['production_capacity_per_month'].items():
            nearby_inventories.append({
                'name': nearby['name'],
                'location': nearby['location'],
                'material': material,
                'quantity': capacity,
                'distance_km': nearby['distance_km']
            })
nearby_inventories_df = pd.DataFrame(nearby_inventories)

shippers_df = pd.DataFrame(warehouse_data['warehouse']['shippers'])

# Load the Llama model
model_path = "models/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf"
llm = Llama(model_path=model_path, n_gpu_layers=-1, n_ctx=20000)

# Set the device to GPU if available
device = 0 if torch.cuda.is_available() else -1

# Initialize the sentiment analysis pipeline with device setting
sentiment_pipeline = pipeline('sentiment-analysis', model="distilbert-base-uncased-finetuned-sst-2-english",
                              device=device)


# Function to generate scenarios using the Llama model
def generate_scenarios(trend_analysis_summary=None):
    prompt = (
        "Given the following warehouse data context:\n"
        f"Sales Data Summary: {sales_data.describe().to_dict()}\n"
        f"Inventory Data Summary: {inventory_df.describe().to_dict()}\n"
        f"Nearby Inventories Data Summary: {nearby_inventories_df.describe().to_dict()}\n"
        f"Shippers Data Summary: {shippers_df.describe().to_dict()}\n"
    )

    # Include trend_analysis_summary in the prompt if it exists
    if trend_analysis_summary:
        prompt += f"Trend Analysis Summary: {trend_analysis_summary}\n"

    prompt += (
        "Analyze the data and suggest 5 potential scenarios that could impact the warehouse operations. "
        "Each scenario should be concise and relevant to the provided data context. "
        "Provide the scenarios in a list format without numbering."
    )

    response = llm(prompt=prompt, temperature=0.5, max_tokens=150, echo=False)
    scenarios_text = response['choices'][0]['text'].strip()

    # Split the response into individual scenarios
    scenarios = [scenario.strip('- ').strip() for scenario in scenarios_text.split('\n') if scenario.strip()]

    # Ensure we have unique and non-empty scenarios
    scenarios = list(filter(None, set(scenarios)))

    # Create options for the dropdown
    scenario_options = [{'label': scenario, 'value': scenario} for scenario in scenarios]

    return scenario_options


# Initialize scenario options
initial_scenario_options = generate_scenarios()

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Styling for section titles
section_title_style = {'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}

# Layout of the app with enhanced styling and new section for scenario simulation
app.layout = html.Div([
    html.H1("Warehouse Inventory Management Dashboard", style={'textAlign': 'center', 'margin-bottom': '40px'}),

    # Inventory Visualization (Collapsible)
    html.Div([
        html.Div([
            html.H2("Current Inventory Levels", style={'margin': 0}),
            dbc.Button("+", id='toggle-inventory', n_clicks=0, className="btn-sm btn-outline-primary")
        ], style=section_title_style),
        dbc.Collapse(
            id='collapse-inventory',
            is_open=False,
            children=[
                dcc.Graph(id='inventory-graph'),
            ]
        )
    ], style={'margin-bottom': '40px'}),

    # Sales Data Visualization (Collapsible)
    html.Div([
        html.Div([
            html.H2("Sales Data", style={'margin': 0}),
            dbc.Button("+", id='toggle-sales', n_clicks=0, className="btn-sm btn-outline-primary")
        ], style=section_title_style),
        dbc.Collapse(
            id='collapse-sales',
            is_open=False,
            children=[
                dcc.Graph(id='sales-graph')
            ]
        )
    ], style={'margin-bottom': '40px'}),

    # Nearby Inventories and Plants (Collapsible)
    html.Div([
        html.Div([
            html.H2("Nearby Inventories and Plants", style={'margin': 0}),
            dbc.Button("+", id='toggle-nearby', n_clicks=0, className="btn-sm btn-outline-primary")
        ], style=section_title_style),
        dbc.Collapse(
            id='collapse-nearby',
            is_open=False,
            children=[
                dcc.Graph(id='nearby-inventories-graph'),
            ]
        )
    ], style={'margin-bottom': '40px'}),

    # Shippers Information (Collapsible)
    html.Div([
        html.Div([
            html.H2("Shippers Information", style={'margin': 0}),
            dbc.Button("+", id='toggle-shippers', n_clicks=0, className="btn-sm btn-outline-primary")
        ], style=section_title_style),
        dbc.Collapse(
            id='collapse-shippers',
            is_open=False,
            children=[
                dcc.Graph(id='shippers-graph'),
            ]
        )
    ], style={'margin-bottom': '40px'}),

    # Upload Trend Report (Collapsible)
    html.Div([
        html.Div([
            html.H2("Upload Trend Report", style={'margin': 0}),
            dbc.Button("+", id='toggle-upload', n_clicks=0, className="btn-sm btn-outline-primary")
        ], style=section_title_style),
        dbc.Collapse(
            id='collapse-upload',
            is_open=False,
            children=[
                dcc.Upload(
                    id='upload-trend-report',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False
                ),
                html.Div(id='output-trend-report')
            ]
        )
    ], style={'margin-bottom': '40px'}),

    # Forecast Visualization (Collapsible)
    html.Div([
        html.Div([
            html.H2("Sales Forecast with Trend Report Integration", style={'margin': 0}),
            dbc.Button("+", id='toggle-forecast', n_clicks=0, className="btn-sm btn-outline-primary")
        ], style=section_title_style),
        dbc.Collapse(
            id='collapse-forecast',
            is_open=True,  # Keep open by default for this section
            children=[
                dcc.Graph(id='forecast-graph'),
                html.Div(id='forecast-justifications', style={'margin-top': '20px'}),
                dbc.Button('Run Forecast', id='run-forecast', n_clicks=0, color="success", className="mt-3")
            ]
        )
    ], style={'margin-bottom': '40px'}),

    # Scenario Simulation and Guidance (Modified Section)
    html.Div([
        html.Div([
            html.H2("Scenario Simulation and Guidance", style={'margin': 0}),
            dbc.Button("⟳", id='refresh-scenarios', n_clicks=0, className="btn-sm btn-outline-secondary",
                       title="Refresh Scenarios"),
            dbc.Button("+", id='toggle-simulation', n_clicks=0, className="btn-sm btn-outline-primary")
        ], style=section_title_style),
        dbc.Collapse(
            id='collapse-simulation',
            is_open=False,
            children=[
                html.Div([
                    html.Label("Select Scenario:"),
                    dcc.Dropdown(
                        id='scenario-dropdown',
                        options=initial_scenario_options,
                        placeholder='Select a scenario',
                        style={'width': '100%'}
                    ),
                    html.Label("Or Enter Your Own Scenario:"),
                    dcc.Textarea(
                        id='manual-scenario',
                        placeholder='Enter custom scenario here...',
                        style={'width': '100%', 'height': '100px', 'margin-top': '10px'}
                    ),
                    dbc.Button('Simulate Scenario', id='run-simulation', n_clicks=0, color="danger", className="mt-3"),
                    html.Div(id='scenario-output', style={'margin-top': '20px'})
                ])
            ]
        )
    ], style={'margin-bottom': '40px'}),

    # Store for forecast data
    dcc.Store(id='forecast-data-store')
])


# Callback to toggle collapsible sections
@app.callback(
    Output('collapse-inventory', 'is_open'),
    Input('toggle-inventory', 'n_clicks'),
    State('collapse-inventory', 'is_open')
)
def toggle_inventory(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output('collapse-sales', 'is_open'),
    Input('toggle-sales', 'n_clicks'),
    State('collapse-sales', 'is_open')
)
def toggle_sales(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output('collapse-nearby', 'is_open'),
    Input('toggle-nearby', 'n_clicks'),
    State('collapse-nearby', 'is_open')
)
def toggle_nearby(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output('collapse-shippers', 'is_open'),
    Input('toggle-shippers', 'n_clicks'),
    State('collapse-shippers', 'is_open')
)
def toggle_shippers(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output('collapse-upload', 'is_open'),
    Input('toggle-upload', 'n_clicks'),
    State('collapse-upload', 'is_open')
)
def toggle_upload(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output('collapse-forecast', 'is_open'),
    Input('toggle-forecast', 'n_clicks'),
    State('collapse-forecast', 'is_open')
)
def toggle_forecast(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output('collapse-simulation', 'is_open'),
    Input('toggle-simulation', 'n_clicks'),
    State('collapse-simulation', 'is_open')
)
def toggle_simulation(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Callback to update scenario options
@app.callback(
    Output('scenario-dropdown', 'options'),
    Input('refresh-scenarios', 'n_clicks'),
    State('output-trend-report', 'children')
)
def update_scenario_options(n_clicks, trend_analysis_summary_div):
    trend_analysis_summary = None
    if trend_analysis_summary_div:
        trend_analysis_summary = trend_analysis_summary_div.children[1].props['children']

    if n_clicks >= 0:
        return generate_scenarios(trend_analysis_summary)
    return initial_scenario_options


# Callback to update inventory graph
@app.callback(
    Output('inventory-graph', 'figure'),
    Input('inventory-graph', 'id')
)
def update_inventory_graph(_):
    fig = px.bar(inventory_df, x='material_name', y='quantity', color='material_name',
                 title='Inventory Levels by Material',
                 labels={'quantity': 'Quantity (Liters)'})
    return fig


# Callback to update sales graph
@app.callback(
    Output('sales-graph', 'figure'),
    Input('sales-graph', 'id')
)
def update_sales_graph(_):
    fig = px.line(sales_data, x='YearMonth', y='Sales', color='Material', markers=True,
                  title='Monthly Sales Data Over the Years')
    fig.update_layout(xaxis=dict(tickangle=-45))

    return fig


@app.callback(
    Output('nearby-inventories-graph', 'figure'),
    Input('nearby-inventories-graph', 'id')
)
def update_nearby_inventories_graph(_):
    records = []

    for nearby in warehouse_data['warehouse']['nearby_inventories']:
        if 'inventory' in nearby:
            for chemical, quantities in nearby['inventory'].items():
                records.append({
                    'Warehouse': nearby.get('name', nearby.get('warehouse_id', 'Unknown')),
                    'Chemical': chemical,
                    'Actual Quantity delivered': quantities.get('Actual Quantity delivered'),
                    'Forecasted Quantity': quantities.get('Forecasted Quantity'),
                    'Location': nearby['location'],
                    'Distance (km)': nearby.get('distance_km')
                })
        elif 'production_capacity_per_month' in nearby:
            for chemical, quantities in nearby['production_capacity_per_month'].items():
                records.append({
                    'Warehouse': nearby.get('name', nearby.get('plant_id', 'Unknown')),
                    'Chemical': chemical,
                    'Actual Quantity delivered': quantities.get('Actual Quantity delivered'),
                    'Forecasted Quantity': quantities.get('Forecasted Quantity'),
                    'Location': nearby['location'],
                    'Distance (km)': nearby.get('distance_km')
                })

    nearby_df = pd.DataFrame(records)

    if nearby_df.empty:
        raise ValueError("The processed nearby_df is empty. Please check the data source.")

    nearby_long_df = pd.melt(
        nearby_df,
        id_vars=['Warehouse', 'Chemical', 'Location', 'Distance (km)'],
        value_vars=['Actual Quantity delivered', 'Forecasted Quantity'],
        var_name='Type',
        value_name='Quantity'
    )

    fig = px.bar(
        nearby_long_df,
        x='Warehouse',
        y='Quantity',
        color='Chemical',
        barmode='group',
        facet_row='Type',
        title='Nearby Inventories: Actual vs Forecasted Quantities',
        hover_data=['Location', 'Distance (km)'],
        labels={'Quantity': 'Quantity (Liters)'}
    )

    return fig


@app.callback(
    Output('shippers-graph', 'figure'),
    Input('shippers-graph', 'id')
)
def update_shippers_graph(_):
    fig = px.bar(shippers_df, x='name', y='reliability_score', color='name',
                 title='Shippers Reliability and Cost',
                 hover_data=['average_delivery_time_days', 'cost_per_km'],
                 labels={'reliability_score': 'Reliability Score'})
    return fig


@app.callback(
    Output('output-trend-report', 'children'),
    Output('forecast-graph', 'figure'),
    Output('forecast-data-store', 'data'),  # Store forecast data
    Input('upload-trend-report', 'contents'),
    Input('run-forecast', 'n_clicks'),
    State('upload-trend-report', 'filename')
)
def analyze_and_forecast(contents, n_clicks, filename):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'upload-trend-report' and contents is not None:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')

            trend_analysis_summary = f"Uploaded file: {filename}"
            fig = px.line(title='Placeholder Forecast Graph')

            return html.Div([html.H5(filename), html.P(trend_analysis_summary)]), fig, None
        except Exception as e:
            return html.Div([html.H5("Error Processing File"), html.P(str(e))]), {}, None

    elif triggered_id == 'run-forecast' and n_clicks > 0:
        try:
            forecast_data = sales_data.groupby('YearMonth')['Sales'].sum().reset_index()
            forecast_data.columns = ['ds', 'y']  # NeuralProphet expects columns 'ds' (date) and 'y' (value)

            model = NeuralProphet(
                seasonality_mode='additive',
                yearly_seasonality=5,
                weekly_seasonality=False,
                daily_seasonality=False,
                n_changepoints=10
            )
            model.fit(forecast_data, freq='M')

            future = model.make_future_dataframe(df=forecast_data, periods=12)
            forecast = model.predict(future)

            fig = px.line(forecast, x='ds', y='yhat1', title='Sales Forecast for Next 12 Months')
            fig.add_scatter(x=forecast_data['ds'], y=forecast_data['y'], mode='markers', name='Actual Sales')

            forecast_data_dict = forecast_data.to_dict('records')

            return "", fig, forecast_data_dict
        except Exception as e:
            return html.Div([html.H5("Error Running Forecast"), html.P(str(e))]), {}, None

    return "", {}, None


from dash.dash_table.Format import Group
from dash import dash_table


@app.callback(
    Output('scenario-output', 'children'),
    Input('run-simulation', 'n_clicks'),
    State('scenario-dropdown', 'value'),
    State('manual-scenario', 'value'),
    State('forecast-data-store', 'data')
)
def simulate_scenario(n_clicks, scenario, manual_scenario, forecast_data):
    if n_clicks > 0 and forecast_data is not None:
        forecast_data_summary = pd.DataFrame(forecast_data).describe().to_dict()
        inventory_summary = inventory_df.describe().to_dict()
        shippers_summary = shippers_df.describe().to_dict()

        selected_scenario = manual_scenario if manual_scenario else scenario

        prompt = (
            f"Given the following scenario: {selected_scenario}. "
            f"Analyze the impact on warehouse inventory, sales forecast, and shippers reliability. "
            f"Provide structured guidance with the following format:\n"
            f"Scenario: {selected_scenario}\n"
            f"Warehouse Inventory Summary: {inventory_summary}\n"
            f"Sales Forecast Summary: {forecast_data_summary}\n"
            f"Shippers Summary: {shippers_summary}\n"
            f"Nearby Inventories situation:{nearby_inventories}"
            "Provide structured guidance for the scenario. Response structure should be {[situation: ..., action plan:..., justification:....], [situation: ..., action plan:..., justification:....]}."
        )

        response = llm(prompt=prompt, temperature=0.5, max_tokens=150, echo=False)
        guidance = response['choices'][0]['text'].strip()

        # Parse the JSON string to a Python list of dictionaries
        try:
            guidance_data = eval(guidance)
        except json.JSONDecodeError as e:
            return html.Div(f"Error parsing JSON: {str(e)}")

        # Normalize JSON keys by ensuring all rows have the same keys
        keys = ["situation", "action plan", "justification"]
        normalized_guidance_data = [{key: d.get(key, '') for key in keys} for d in guidance_data]

        # Convert to a DataFrame for easier handling in Dash
        guidance_df = pd.DataFrame(normalized_guidance_data)

        return html.Div([
            html.H5("Scenario Guidance"),
            dash_table.DataTable(
                data=guidance_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in guidance_df.columns],
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'font-family': 'Arial',
                    'font-size': '14px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': '#4CAF50',
                    'fontWeight': 'bold',
                    'color': 'white',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9',
                    }
                ],
                style_table={
                    'margin-top': '20px',
                    'width': '100%',
                    'overflowX': 'auto',
                },
                merge_duplicate_headers=True
            )
        ])
    return html.Div("Please run the forecast before simulating a scenario.")


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
