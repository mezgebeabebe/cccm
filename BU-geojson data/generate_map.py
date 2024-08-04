import folium
import json
import pandas as pd

# Load the GeoJSON files
with open('woreda.geojson') as f:
    woreda_geojson = json.load(f)

with open('sites.geojson') as f:
    sites_geojson = json.load(f)

# Convert woreda_geojson features to a DataFrame to extract unique values for filtering
woreda_df = pd.json_normalize(woreda_geojson['features'])

# Create a Folium map centered around a specific location
m = folium.Map(location=[9.145, 40.489673], zoom_start=6)

# Add the sites layer to the map
folium.GeoJson(sites_geojson, name="Sites", control=False).add_to(m)

# Function to add the woreda layer to the map and symbolize based on a column
def add_woreda_layer(map_obj, woreda_geojson, column=None, value=None):
    def style_function(feature):
        # Default color is grey
        fill_color = 'grey'
        if column and feature['properties'][column] == value:
            fill_color = 'yellow'
        return {
            'fillColor': fill_color,
            'color': 'blue',
            'weight': 2,
            'dashArray': '5, 5'
        }

    folium.GeoJson(woreda_geojson, name="Woreda", style_function=style_function, control=False).add_to(map_obj)

# Initially add the woreda layer without filtering
add_woreda_layer(m, woreda_geojson)

# Save the map to an HTML file with initial layers
m.save('map.html')
