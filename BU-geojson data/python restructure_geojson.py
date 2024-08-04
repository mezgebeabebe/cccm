import folium
import json
import pandas as pd

# Load the GeoJSON files
with open('woreda_restructured.geojson') as f:
    woreda_geojson = json.load(f)

with open('sites_restructured.geojson') as f:
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

    # Function to bind popups to features
    def on_each_feature(feature, layer):
        popup_content = "<b>Feature Info:</b><br>" + json.dumps(feature['properties'], indent=2)
        layer.bindPopup(popup_content)
        layer.on({
            'click': lambda e: e.target.openPopup()  # Open popup on click
        })

    folium.GeoJson(
        woreda_geojson,
        name="Woreda",
        style_function=style_function,
        on_each_feature=on_each_feature,
        control=False
    ).add_to(map_obj)

# Initially add the woreda layer without filtering
add_woreda_layer(m, woreda_geojson)

# Save the map to an HTML file with initial layers
m.save('map.html')

# JavaScript code for interactivity with blinking effect and feature info display
js_code = """
<script>
function getColor(isSelected) {
    return isSelected ? '#ffff00' : '#ffaf00'; // Yellow if selected, otherwise default color
}

function updateMap() {
    var column = document.getElementById('columnDropdown').value;
    var value = document.getElementById('valueDropdown').value;
    
    console.log('Selected column:', column);
    console.log('Selected value:', value);
    
    for (var i in window.mapLayers) {
        window.map.removeLayer(window.mapLayers[i]);
    }

    fetch('woreda_restructured.geojson')
        .then(response => response.json())
        .then(data => {
            var filteredFeatures = data.features.filter(function(feature) {
                return feature.properties[column] == value;
            });

            console.log('Filtered features:', filteredFeatures);

            var filteredGeoJson = {
                "type": "FeatureCollection",
                "features": filteredFeatures
            };

            var geojsonLayer = L.geoJson(filteredGeoJson, {
                style: function(feature) {
                    return {
                        fillColor: getColor(true),
                        color: 'blue',
                        weight: 2,
                        dashArray: '5, 5'
                    };
                },
                onEachFeature: function (feature, layer) {
                    var popupContent = "<b>Feature Info:</b><br>" + JSON.stringify(feature.properties, null, 2);
                    layer.bindPopup(popupContent);
                    layer.on({
                        click: function(e) {
                            e.target.openPopup(); // Open the popup when the feature is clicked
                        }
                    });
                }
            });

            geojsonLayer.addTo(window.map);
            window.mapLayers.push(geojsonLayer);

            if (filteredFeatures.length > 0) {
                var bbox = geojsonLayer.getBounds();
                window.map.fitBounds(bbox); // Zoom to fit the filtered features
            }
            blinkFeatures(geojsonLayer);
        });
}

function blinkFeatures(layer) {
    var interval = setInterval(function() {
        layer.setStyle({
            fillColor: layer.options.style.fillColor === '#ffff00' ? '#ffaf00' : '#ffff00'
        });
    }, 500); // Blink every 500 milliseconds

    setTimeout(function() {
        clearInterval(interval); // Stop blinking after 5 seconds
        layer.setStyle({
            fillColor: '#ffff00'
        });
    }, 5000); // Stop blinking after 5 seconds
}

document.addEventListener('DOMContentLoaded', function() {
    window.map = L.map('mapid').setView([9.145, 40.489673], 6);
    window.mapLayers = [];

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(window.map);

    fetch('woreda_restructured.geojson')
        .then(response => response.json())
        .then(data => {
            var geojsonLayer = L.geoJson(data, {
                style: function(feature) {
                    return {
                        fillColor: '#ffaf00',
                        color: 'blue',
                        weight: 2,
                        dashArray: '5, 5'
                    };
                },
                onEachFeature: function (feature, layer) {
                    var popupContent = "<b>Feature Info:</b><br>" + JSON.stringify(feature.properties, null, 2);
                    layer.bindPopup(popupContent);
                    layer.on({
                        click: function(e) {
                            e.target.openPopup(); // Open the popup when the feature is clicked
                        }
                    });
                }
            });

            geojsonLayer.addTo(window.map);
            window.mapLayers.push(geojsonLayer);
        });

    fetch('sites_restructured.geojson')
        .then(response => response.json())
        .then(data => {
            var geojsonLayer = L.geoJson(data);
            geojsonLayer.addTo(window.map);
            window.mapLayers.push(geojsonLayer);
        });

    updateValueDropdown();
});

function updateValueDropdown() {
    var column = document.getElementById('columnDropdown').value;
    fetch('woreda_restructured.geojson')
        .then(response => response.json())
        .then(data => {
            console.log('GeoJSON data:', data);
            var uniqueValues = [...new Set(data.features.map(feature => feature.properties[column]))];
            console.log('Unique values for column', column, ':', uniqueValues);
            var valueDropdown = document.getElementById('valueDropdown');
            valueDropdown.innerHTML = '';

            uniqueValues.forEach(function(value) {
                var option = document.createElement('option');
                option.value = value;
                option.text = value;
                valueDropdown.appendChild(option);
            });

            if (uniqueValues.length > 0) {
                valueDropdown.value = uniqueValues[0];
                updateMap();
            }
        })
        .catch(error => {
            console.error('Error updating value dropdown:', error);
        });
}
</script>
"""

# Create HTML dropdowns
column_options = [col.split('.')[-1] for col in woreda_df.columns if col.startswith('properties.')]
dropdown_html = f"""
<div style="position: fixed; top: 10px; left: 10px; z-index: 9999; background-color: white; padding: 10px; border-radius: 5px;">
    <label for="columnDropdown">Column:</label>
    <select id="columnDropdown" onchange="updateValueDropdown()">
        {''.join(f'<option value="{option}">{option}</option>' for option in column_options)}
    </select>
    <br>
    <label for="valueDropdown">Value:</label>
    <select id="valueDropdown" onchange="updateMap()">
        <!-- Options will be dynamically populated -->
    </select>
</div>
"""

# Read the existing map HTML file
with open('map.html', 'r') as file:
    map_html = file.read()

# Insert the dropdowns and JavaScript into the HTML file
final_html = map_html.replace('<body>', f'<body>{dropdown_html}{js_code}')

# Write the final HTML to file
with open('map.html', 'w') as file:
    file.write(final_html)
