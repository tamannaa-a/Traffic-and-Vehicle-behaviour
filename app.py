import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static

st.set_page_config(page_title="🌐 Futuristic Traffic Map", layout="wide")
st.title("🚦 Futuristic Traffic Density Visualization")

uploaded_file = st.file_uploader("📁 Upload futuristic_city_traffic.csv", type=["csv"])

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)

    required_cols = [
        'City', 'Vehicle Type', 'Weather', 'Hour Of Day',
        'Speed', 'Traffic Density', 'Energy Consumption'
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Your CSV is missing required columns: {missing_cols}")
        st.stop()

    # Convert numeric density to categories
    def categorize_density(val):
        if val < 0.33:
            return 'Low'
        elif val < 0.66:
            return 'Medium'
        else:
            return 'High'

    df['Density Category'] = df['Traffic Density'].apply(categorize_density)

    # Simulated GPS for fictional cities
    city_coords = {
        'SolarisVille': (37.77, -122.42),
        'AquaCity': (34.05, -118.24),
        'Neuroburg': (40.71, -74.01),
        'Ecoopolis': (41.88, -87.62)
    }
    df['Latitude'] = df['City'].map(lambda x: city_coords.get(x, (None, None))[0])
    df['Longitude'] = df['City'].map(lambda x: city_coords.get(x, (None, None))[1])

    return df.dropna(subset=['Latitude', 'Longitude'])

if uploaded_file:
    df = load_data(uploaded_file)

    density_map = {'Low': 1, 'Medium': 2, 'High': 3}
    color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
    df['Weight'] = df['Density Category'].map(density_map)

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        selected_cities = st.multiselect("City", df['City'].unique(), default=df['City'].unique())
        selected_vehicles = st.multiselect("Vehicle Type", df['Vehicle Type'].unique(), default=df['Vehicle Type'].unique())
        selected_weather = st.multiselect("Weather", df['Weather'].unique(), default=df['Weather'].unique())
        selected_density = st.multiselect("Traffic Level", df['Density Category'].unique(), default=df['Density Category'].unique())
        hour_range = st.slider("Hour of Day", 0, 23, (0, 23))

    filtered_df = df[
        df['City'].isin(selected_cities) &
        df['Vehicle Type'].isin(selected_vehicles) &
        df['Weather'].isin(selected_weather) &
        df['Density Category'].isin(selected_density) &
        df['Hour Of Day'].between(hour_range[0], hour_range[1])
    ]

    # Map
    st.subheader("🗺️ Interactive Traffic Map")
    map_center = [filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=5)

    heat_data = [[row['Latitude'], row['Longitude'], row['Weight']] for _, row in filtered_df.iterrows()]
    HeatMap(heat_data, radius=15, blur=10, min_opacity=0.3).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for _, row in filtered_df.iterrows():
        popup = f"""
        City: {row['City']}<br>
        Vehicle: {row['Vehicle Type']}<br>
        Weather: {row['Weather']}<br>
        Hour: {row['Hour Of Day']}<br>
        Speed: {row['Speed']}<br>
        Density: {row['Density Category']}
        """
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            color=color_map.get(row['Density Category'], 'gray'),
            fill=True,
            fill_opacity=0.8,
            popup=popup
        ).add_to(marker_cluster)

    with st.expander("🧭 Legend"):
        st.markdown("""
        - 🟢 **Low Traffic**  
        - 🟠 **Medium Traffic**  
        - 🔴 **High Traffic**
        """)

    folium_static(m)
    st.download_button("⬇️ Download Filtered CSV", filtered_df.to_csv(index=False), file_name="filtered_futuristic_traffic.csv")

else:
    st.info("Please upload futuristic_city_traffic.csv to visualize traffic data.")
