import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
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

    # Traffic density to weight and color mapping
    density_map = {'Low': 1, 'Medium': 2, 'High': 3}
    color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
    df['Weight'] = df['Traffic Density'].map(density_map)

    # Filters
    with st.sidebar:
        st.header("🔍 Filters")
        selected_cities = st.multiselect("Select Cities", df['City'].unique(), default=df['City'].unique())
        selected_density = st.multiselect("Traffic Level", df['Traffic Density'].unique(), default=df['Traffic Density'].unique())
        selected_hour = st.slider("Hour of Day", 0, 23, (0, 23))

    filtered_df = df[
        (df['City'].isin(selected_cities)) &
        (df['Traffic Density'].isin(selected_density)) &
        (df['Hour Of Day'].between(selected_hour[0], selected_hour[1]))
    ]

    # Map initialization
    st.subheader("🗺️ Interactive Traffic Map")
    map_center = [filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=5)

    # Add Heatmap
    heat_data = [[row['Latitude'], row['Longitude'], row['Weight']] for _, row in filtered_df.iterrows()]
    HeatMap(heat_data, radius=15, blur=10, min_opacity=0.3).add_to(m)

    # Add Clustered Circle Markers
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in filtered_df.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            color=color_map.get(row['Traffic Density'], 'gray'),
            fill=True,
            fill_opacity=0.8,
            popup=f"{row['City']}\n{row['Traffic Density']}\nSpeed: {row['Speed']}\nHour: {row['Hour Of Day']}"
        ).add_to(marker_cluster)

    # Display legend
    with st.expander("🧭 Legend"):
        st.markdown("""
        - 🟢 **Low Traffic**
        - 🟠 **Medium Traffic**
        - 🔴 **High Traffic**
        """)

    folium_static(m)

    # Export
    st.download_button("⬇️ Download Filtered CSV", filtered_df.to_csv(index=False), file_name="filtered_traffic.csv")

else:
    st.info("Please upload a CSV file to visualize traffic density on the map.")
