import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

st.set_page_config(page_title="🚦 Traffic Density Map", layout="wide")
st.title("🗺️ Real-Time Traffic Density Visualizer")

# Upload section
uploaded_file = st.file_uploader("📁 Upload CSV with Latitude, Longitude & Density columns", type=["csv"])

with st.expander("📌 CSV Format Instructions"):
    st.markdown("""
    Ensure your CSV contains the following columns:
    - **Location**: Any location name (optional but useful for popup)
    - **Latitude**: Decimal latitude
    - **Longitude**: Decimal longitude
    - **Density**: One of ['Low', 'Medium', 'High']
    """)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Validate columns
    required_cols = ['Location', 'Latitude', 'Longitude', 'Density']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing columns. Required: {', '.join(required_cols)}")
    else:
        st.success("✅ File successfully uploaded!")

        # Density to weight & color
        density_map = {'Low': 1, 'Medium': 2, 'High': 3}
        color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        df['Weight'] = df['Density'].map(density_map)

        # Create map centered on average location
        m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=13)

        # Add HeatMap
        heat_data = [[row['Latitude'], row['Longitude'], row['Weight']] for _, row in df.iterrows()]
        HeatMap(heat_data, radius=20, blur=15, min_opacity=0.4).add_to(m)

        # Add color-coded markers
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=(row['Latitude'], row['Longitude']),
                radius=10,
                color=color_map[row['Density']],
                fill=True,
                fill_color=color_map[row['Density']],
                fill_opacity=0.8,
                popup=f"{row['Location']} - {row['Density']} Traffic"
            ).add_to(m)

        # Display map
        st.subheader("🔍 Interactive Traffic Density Map")
        folium_static(m)
else:
    st.info("Upload a CSV to visualize traffic density on the map.")
