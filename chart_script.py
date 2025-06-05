import plotly.graph_objects as go
import pandas as pd

# Data for the architecture diagram
data = {
    "components": [
        {"name": "florist.inspiro.pro", "type": "data_source", "x": 1, "y": 1},
        {"name": "Google Sheets", "type": "data_source", "x": 1, "y": 2},
        {"name": "OpenWeatherMap API", "type": "data_source", "x": 1, "y": 3},
        {"name": "Kazakhstan Holidays", "type": "data_source", "x": 1, "y": 4},
        
        {"name": "Integration Layer", "type": "processing", "x": 2, "y": 1.5},
        {"name": "Error Handling", "type": "processing", "x": 2, "y": 2.5},
        {"name": "ML Models", "type": "processing", "x": 2, "y": 3.5},
        {"name": "Multi-Store Manager", "type": "processing", "x": 3, "y": 2.5},
        
        {"name": "Streamlit App", "type": "interface", "x": 4, "y": 1.5},
        {"name": "Google Sheets UI", "type": "interface", "x": 4, "y": 2.5},
        {"name": "Corrections System", "type": "interface", "x": 4, "y": 3.5},
        
        {"name": "Store Forecasts", "type": "output", "x": 5, "y": 1},
        {"name": "Purchase Recommendations", "type": "output", "x": 5, "y": 2},
        {"name": "Analytics Reports", "type": "output", "x": 5, "y": 3},
        {"name": "Multi-Store Insights", "type": "output", "x": 5, "y": 4}
    ]
}

# Convert to DataFrame
df = pd.DataFrame(data['components'])

# Define colors for each component type
color_map = {
    'data_source': '#1FB8CD',    # Strong cyan
    'processing': '#FFC185',     # Light orange  
    'interface': '#ECEBD5',      # Light green
    'output': '#5D878F'          # Cyan
}

# Create figure
fig = go.Figure()

# Add components as scatter points with rounded rectangles
for comp_type in df['type'].unique():
    type_data = df[df['type'] == comp_type]
    
    # Shorten names to fit 15 character limit
    shortened_names = []
    for name in type_data['name']:
        if len(name) <= 15:
            shortened_names.append(name)
        else:
            # Abbreviate long names
            if name == "florist.inspiro.pro":
                shortened_names.append("Florist System")
            elif name == "OpenWeatherMap API":
                shortened_names.append("Weather API")
            elif name == "Kazakhstan Holidays":
                shortened_names.append("Holidays API")
            elif name == "Integration Layer":
                shortened_names.append("Integration")
            elif name == "Error Handling":
                shortened_names.append("Error Handler")
            elif name == "Multi-Store Manager":
                shortened_names.append("Multi-Store Mgr")
            elif name == "Google Sheets UI":
                shortened_names.append("Sheets UI")
            elif name == "Corrections System":
                shortened_names.append("Corrections")
            elif name == "Store Forecasts":
                shortened_names.append("Forecasts")
            elif name == "Purchase Recommendations":
                shortened_names.append("Purchase Rec.")
            elif name == "Analytics Reports":
                shortened_names.append("Analytics")
            elif name == "Multi-Store Insights":
                shortened_names.append("Store Insights")
            else:
                shortened_names.append(name[:15])
    
    fig.add_trace(go.Scatter(
        x=type_data['x'],
        y=type_data['y'],
        mode='markers+text',
        marker=dict(
            size=100,  # Increased size
            color=color_map[comp_type],
            symbol='square',
            line=dict(width=3, color='white')
        ),
        text=shortened_names,
        textposition='middle center',
        textfont=dict(size=12, color='black', family='Arial Black'),  # Increased font size and weight
        name=comp_type.replace('_', ' ').title(),
        cliponaxis=False
    ))

# Improved arrow connections with better routing to minimize overlaps
arrow_connections = [
    # Data sources to integration layer (staggered connections)
    [(1, 1), (1.7, 1.3), (2, 1.5)],     # Florist system with curve
    [(1, 2), (1.7, 1.7), (2, 1.5)],     # Google Sheets with curve
    [(1, 3), (1.7, 2.8), (2, 2.5)],     # Weather API with curve
    [(1, 4), (1.7, 3.2), (2, 2.5)],     # Holidays API with curve
    
    # Processing layer connections (vertical flow)
    [(2, 1.5), (2, 2.5)],               # Integration to Error Handling
    [(2, 2.5), (2, 3.5)],               # Error Handling to ML Models
    [(2, 3.5), (2.5, 3.0), (3, 2.5)],   # ML Models to Multi-Store Manager with curve
    
    # Processing to interface (staggered)
    [(3, 2.5), (3.7, 2.0), (4, 1.5)],   # Multi-Store to Streamlit with curve
    [(3, 2.5), (4, 2.5)],               # Multi-Store to Sheets UI direct
    [(3, 2.5), (3.7, 3.0), (4, 3.5)],   # Multi-Store to Corrections with curve
    
    # Interface to outputs (staggered)
    [(4, 1.5), (4.7, 1.2), (5, 1)],     # Streamlit to Forecasts with curve
    [(4, 2.5), (4.7, 2.2), (5, 2)],     # Sheets UI to Purchase Rec with curve
    [(4, 3.5), (4.7, 3.2), (5, 3)],     # Corrections to Analytics with curve
    [(4, 2.5), (4.7, 3.2), (5, 4)]      # Sheets UI to Multi-Store Insights with curve
]

# Add arrows as lines with curves for better visibility
for connection in arrow_connections:
    if len(connection) == 2:  # Direct line
        start, end = connection
        fig.add_trace(go.Scatter(
            x=[start[0], end[0]],
            y=[start[1], end[1]],
            mode='lines',
            line=dict(color='#666666', width=3),  # Thicker lines
            showlegend=False,
            cliponaxis=False
        ))
    elif len(connection) == 3:  # Curved line
        start, mid, end = connection
        fig.add_trace(go.Scatter(
            x=[start[0], mid[0], end[0]],
            y=[start[1], mid[1], end[1]],
            mode='lines',
            line=dict(color='#666666', width=3, shape='spline'),  # Curved lines
            showlegend=False,
            cliponaxis=False
        ))

# Add arrow heads for better direction indication
arrow_heads = [
    # Key arrows to show direction
    (1.9, 1.5), (1.9, 2.5), (2.9, 2.5), (3.9, 1.5), (3.9, 2.5), (3.9, 3.5), (4.9, 1), (4.9, 2), (4.9, 3), (4.9, 4)
]

for x, y in arrow_heads:
    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode='markers',
        marker=dict(
            size=12,
            color='#666666',
            symbol='triangle-right'
        ),
        showlegend=False,
        cliponaxis=False
    ))

# Update layout with better alignment
fig.update_layout(
    title="Sales Forecast System Architecture",
    xaxis=dict(
        title="System Layers",
        tickmode='array',
        tickvals=[1, 2, 3, 4, 5],
        ticktext=['Data Sources', 'Processing', 'Core Logic', 'Interface', 'Outputs'],
        range=[0.3, 5.7],
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1
    ),
    yaxis=dict(
        title="Components",
        showticklabels=False,
        range=[0.3, 4.7],
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1
    ),
    legend=dict(
        orientation='h', 
        yanchor='bottom', 
        y=1.05, 
        xanchor='center', 
        x=0.5
    ),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Save the chart
fig.write_image("sales_forecast_architecture.png")