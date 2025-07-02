import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

st.set_page_config(page_title="📍 Traffic Density Map", layout="wide")
st.title("🚦 Traffic Density Visualization from Dataset")

# Load the static dataset (dt.csv)
@st.cache_data
def load_data():
    df = pd.read_csv("dt.csv")

    # Map simulated GPS coordinates by city
    city_to_coords = {
        'New York': (40.7128, -74.0060),
        'Los Angeles': (34.0522, -118.2437),
        'Chicago': (41.8781, -87.6298),
        'Houston': (29.7604, -95.3698),
        'San Francisco': (37.7749, -122.4194)
    }

    df['Latitude'] = df['City'].map(lambda x: city_to_coords.get(x, (None, None))[0])
    df['Longitude'] = df['City'].map(lambda x: city_to_coords.get(x, (None, None))[1])

    return df.dropna(subset=['Latitude', 'Longitude'])

# Load data
df = load_data()

# Map density to visual features
density_map = {'Low': 1, 'Medium': 2, 'High': 3}
color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
df['Weight'] = df['Traffic Density'].map(density_map)

# Show data preview
with st.expander("🔍 Preview Dataset"):
    st.dataframe(df[['City', 'Latitude', 'Longitude', 'Traffic Density', 'Speed']])

# Create map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# Heatmap Layer
heat_data = [[row['Latitude'], row['Longitude'], row['Weight']] for _, row in df.iterrows()]
HeatMap(heat_data, radius=15, blur=10, min_opacity=0.3).add_to(m)

# Marker Layer
for _, row in df.iterrows():
    folium.CircleMarker(
        location=(row['Latitude'], row['Longitude']),
        radius=6,
        color=color_map[row['Traffic Density']],
        fill=True,
        fill_opacity=0.9,
        popup=f"{row['City']} - {row['Traffic Density']} Traffic"
    ).add_to(m)

# Display map
st.subheader("🗺️ Interactive Traffic Map")
folium_static(m)

st.caption("Data sourced from dt.csv | GPS is simulated based on city")
