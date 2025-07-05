import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

st.set_page_config(page_title="📍 Traffic Density Map", layout="wide")
st.title("🚦 Traffic Density Mapping")

uploaded_file = st.file_uploader("📁 Upload your traffic dataset (CSV)", type=["csv"])

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)

    required_cols = ['City', 'Traffic Density', 'Speed', 'Hour Of Day', 'Energy Consumption']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Your CSV is missing required columns: {missing_cols}")
        st.stop()

    df['City'] = df['City'].str.strip().str.title()

    city_to_coords = {
        'New York': (40.7128, -74.0060),
        'Los Angeles': (34.0522, -118.2437),
        'Chicago': (41.8781, -87.6298)
    }

    df['Latitude'] = df['City'].map(lambda x: city_to_coords.get(x, (None, None))[0])
    df['Longitude'] = df['City'].map(lambda x: city_to_coords.get(x, (None, None))[1])

    return df.dropna(subset=['Latitude', 'Longitude'])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    density_map = {'Low': 1, 'Medium': 2, 'High': 3}
    color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
    df['Weight'] = df['Traffic Density'].map(density_map)

    st.subheader("🗺️ Interactive Traffic Map")
    theme = st.selectbox("Choose Map Theme", ["OpenStreetMap", "CartoDB positron", "Stamen Toner", "Stamen Terrain"])
    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=5, tiles=theme)

    heat_data = [[row['Latitude'], row['Longitude'], row['Weight']] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=15, blur=10, min_opacity=0.3).add_to(m)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            color=color_map.get(row['Traffic Density'], 'gray'),
            fill=True,
            fill_opacity=0.8,
            popup=f"{row['City']} - {row['Traffic Density']}"
        ).add_to(m)

    folium_static(m)
else:
    st.info("Please upload a CSV file to visualize traffic density on the map.")
