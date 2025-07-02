import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

st.set_page_config(page_title="📍 Traffic Density Map", layout="wide")
st.title("🚦 Traffic Density Prediction & Visualization")

st.markdown("""
This project uses a dataset containing urban traffic sensor readings (e.g., vehicle counts, speeds, and contextual factors) to build machine learning models for predicting traffic density. 

The models will uncover **mobility insights**, such as how weather, peak hours, or random events affect traffic conditions across cities like **New York, Los Angeles, and Chicago**. 

These insights can guide:
- 🚦 Traffic signal optimization
- 🚗 Route planning
- 🏛️ Urban mobility policy decisions
""")

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
    st.dataframe(df)

# ----------------------------
# 📊 INSIGHT: Weather & Hour Impact
# ----------------------------
st.subheader("📊 Mobility Insight Analysis")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Traffic Density by Weather**")
    fig1 = plt.figure(figsize=(6,3))
    sns.countplot(data=df, x='Weather', hue='Traffic Density')
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with col2:
    st.markdown("**Traffic Density by Hour**")
    fig2 = plt.figure(figsize=(6,3))
    sns.countplot(data=df, x='Hour Of Day', hue='Traffic Density')
    st.pyplot(fig2)

# ----------------------------
# 🤖 ML Model
# ----------------------------
st.subheader("🤖 Predict Traffic Density")
features = ['Speed', 'Vehicle Count', 'Hour Of Day', 'Energy Consumption']
X = df[features]
y = df['Traffic Density']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
model = RandomForestClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

st.markdown("**Model Evaluation**")
st.text("Classification Report")
st.text(classification_report(y_test, y_pred))

# ----------------------------
# 🗺️ Interactive Map
# ----------------------------
st.subheader("🗺️ Interactive Traffic Map")
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

folium_static(m)

st.caption("Data sourced from dt.csv | GPS is simulated based on city")
