import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

# Set Streamlit page settings
st.set_page_config(page_title="📍 Traffic Density Map", layout="wide")
st.title("🚦 Traffic Density Visualization")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("dt.csv")

    # Add simulated GPS coordinates for cities
    city_to_coords = {
        'New York': (40.7128, -74.0060),
        'Los Angeles': (34.0522, -118.2437),
        'Chicago': (41.8781, -87.6298),
        'Houston': (29.7604, -95.3698),
        'San Francisco': (37.7749, -122.4194)
    }

    df['Latitude'] = df['City'].map(lambda x: city_to_coords.get(x, (None, None))[0])
    df['Longitude'] = df['City'].map(lambda x: city_to_coords.get(x, (None, None))[1])

    # Drop entries without coordinates
    df = df.dropna(subset=['Latitude', 'Longitude'])

    return df

# Load and process data
df = load_data()

# Map traffic density to weights and colors
density_map = {'Low': 1, 'Medium': 2, 'High': 3}
color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
df['Weight'] = df['Traffic Density'].map(density_map)

# Show preview
with st.expander("🔍 Preview Data"):
    st.dataframe(df[['City', 'Traffic Density', 'Speed', 'Latitude', 'Longitude']])

# Create base map
map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=5)

# Add heatmap layer
heat_data = [[row['Latitude'], row['Longitude'], row['Weight']] for _, row in df.iterrows()]
HeatMap(heat_data, radius=15, blur=10, min_opacity=0.3).add_to(m)

# Add circle markers
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=6,
        color=color_map[row['Traffic Density']],
        fill=True,
        fill_color=color_map[row['Traffic Density']],
        fill_opacity=0.8,
        popup=f"{row['City']} - {row['Traffic Density']}"
    ).add_to(m)

# Display map
st.subheader("🗺️ Interactive Traffic Map")
folium_static(m)

st.caption("Note: GPS coordinates are simulated based on city names.")
