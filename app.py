import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_elements import elements, mui, html
from streamlit_elements import nivo

# Page configuration
st.set_page_config(
    page_title="US Population Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# setting a session state variable to track the current mode
if 'mode' not in st.session_state:
    st.session_state.mode = "dark"  # Always start in dark mode

# Function to change tooltip colors based on app theme
def theme_check():
    if st.session_state.mode == "dark":
        return {
            "background": "transparent",  # No background
            "textColor": "#fafafa",
            "tooltip": {
                "container": {
                    "background": "black",  # No background for tooltip
                    "color": "#fff",  # white text color in dark mode
                    "border": "solid 3px #F0F2F6",
                    "border-radius": "8px",
                    "padding": 5,
                }
            }
        }
    else:
        return {
            "background": "white",  # No background
            "textColor": "#000000",
            "tooltip": {
                "container": {
                    "background-color": "#fff",  # No background for tooltip
                    "color": "#000000",  # Text color in light mode
                    "border": "solid 3px #262730",
                    "border-radius": "8px",
                }
            }
        }

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/us-population-2010-2019-reshaped.csv')

df_reshaped = load_data()

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    # Year selector
    year_list = sorted(df_reshaped.year.unique(), reverse=True)
    selected_year = st.selectbox('Select Year', year_list, key='year_select', label_visibility='collapsed')
    
    # Filter data for selected year
    df_selected = df_reshaped[df_reshaped.year == selected_year].copy()
    
    # Key metrics
    total_pop = df_selected['population'].sum()
    
    # Format total population with commas
    total_pop = f"{total_pop:,}"  # Add commas here
    
    # Display total population with formatted value
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_pop}</div>  <!-- Use the formatted total population here -->
            <div class="metric-label">Total Population</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Population by Region Pie Chart (keep raw numbers for pie chart)
    regions = {
        'Northeast': ['ME', 'NH', 'VT', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA'],
        'Midwest': ['OH', 'IN', 'IL', 'MI', 'WI', 'MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS'],
        'South': ['DE', 'MD', 'DC', 'VA', 'WV', 'NC', 'SC', 'GA', 'FL', 'KY', 'TN', 'AL', 'MS', 'AR', 'LA', 'OK', 'TX'],
        'West': ['MT', 'ID', 'WY', 'CO', 'NM', 'AZ', 'UT', 'NV', 'WA', 'OR', 'CA', 'AK', 'HI']
    }
    
    # Transform data for Nivo (keep raw population values)
    region_data = []
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    for i, (region, states) in enumerate(regions.items()):
        pop = int(df_selected[df_selected['states_code'].isin(states)]['population'].sum())
        formatted_pop = f"{pop:,}"  # Format the population with commas here
        region_data.append({
            "id": region,
            "label": region,
            "value": pop,  # Numerical value for chart rendering
            "color": colors[i % len(colors)],
            "formatted_value": formatted_pop  # Formatted string value with commas
        })

    # Nivo Pie Chart (show formatted population values)
    with elements("nivo_pie_chart"):
        with mui.Box(sx={"height": 300}):
            nivo.Pie(
                data=region_data,
                margin={"top": 40, "right": 40, "bottom": 40, "left": 40},
                innerRadius=0.5,
                padAngle=0.7,
                cornerRadius=3,
                activeOuterRadiusOffset=8,
                borderWidth=1,
                borderColor={"from": "color", "modifiers": [["darker", 0.2]]},
                arcLinkLabelsSkipAngle=10,
                arcLinkLabelsTextColor="#e5e7eb",
                arcLinkLabelsThickness=2,
                arcLinkLabelsColor={"from": "color"},
                arcLabelsSkipAngle=10,
                arcLabelsTextColor={"from": "color", "modifiers": [["darker", 4]]},
                theme=theme_check(),
                defs=[{
                    "id": "dots",
                    "type": "patternDots",
                    "background": "inherit",
                    "color": "rgba(255, 255, 255, 0.3)",
                    "size": 4,
                    "padding": 1,
                    "stagger": True,
                }, {
                    "id": "lines",
                    "type": "patternLines",
                    "background": "inherit",
                    "color": "rgba(255, 255, 255, 0.3)",
                    "rotation": -45,
                    "lineWidth": 6,
                    "spacing": 10,
                }], 
                fill=[{"match": {"id": region}, "id": "dots"} for region in regions.keys()],
                legends=[{
                    "anchor": "bottom",
                    "direction": "row",
                    "justify": False,
                    "translateX": 0,
                    "translateY": 30,
                    "itemsSpacing": 0,
                    "itemWidth": 80,
                    "itemHeight": 18,
                    "itemTextColor": "#999",
                    "itemDirection": "left-to-right",
                    "itemOpacity": 1,
                    "symbolSize": 18,
                    "symbolShape": "circle",
                    "effects": [{"on": "hover", "style": {"itemTextColor": "#fff"}}],
                }],
                labelFormat = lambda value: region_data[value]["formatted_value"]  # Display formatted population
            )

    # Top 10 States (horizontal bar chart)
    top_10_states = df_selected.nlargest(10, 'population')
    fig_bars = go.Figure(data=[go.Bar(
        y=top_10_states['states'],
        x=top_10_states['population'],
        orientation='h',
        marker_color=px.colors.sequential.Blues[::2]
    )])



    fig_bars.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        xaxis_title="Population",
        yaxis_title="",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickformat=".2s")  # Format the population in a human-readable way (e.g., 1M, 10B)
    )
    st.plotly_chart(fig_bars, use_container_width=True)



with col2:
    # US Map (Choropleth)
    fig_map = go.Figure(data=go.Choropleth(
        locations=df_selected['states_code'],
        z=df_selected['population'],
        locationmode='USA-states',
        colorscale='magma',
        colorbar_title="Population"
    ))

    fig_map.update_layout(
        geo_scope='usa',
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        geo=dict(
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Population Trend Line
    df_trend = df_reshaped.groupby('year')['population'].sum().reset_index()
    fig_trend = px.line(df_trend, x='year', y='population', title='Population Trend Over Time')

    fig_trend.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=200,
        xaxis_title="Year",
        yaxis_title="Population",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(tickformat=".2s")  # Format the population in a human-readable way (e.g., 1M, 10B)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# Hide Streamlit branding
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
#GithubIcon {
    visibility: visible;
}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
# Add custom CSS styles
st.write(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        font-size: 20px;
        color: #333;
    }
    .stMetricValue {
        font-size: 24px;
        font-weight: bold;
    }
    .stMetricLabel {
        font-size: 20px;
        color: #666;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Footer
st.markdown("---")
st.markdown("Data Source: US Census Bureau")
