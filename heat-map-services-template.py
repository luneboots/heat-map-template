import pandas as pd
import folium
from folium.plugins import HeatMap
import googlemaps
from geopy.distance import geodesic

gmaps = googlemaps.Client(key='YOUR API KEY FROM GOOGLE MAPS')

def geocode_address(address):
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocode was not successful for the following reason: {geocode_result}")
            return None, None
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None, None

locations_df = pd.read_excel('YOUR PATH.XLSX')
msa_cities_df = pd.read_excel('YOUR PATH.XLSX')

msa_cities = []
for index, row in msa_cities_df.iterrows():
    city_state = f"{row['CITY']}, {row['STATE']}"
    lat, lng = geocode_address(city_state)
    if lat is not None and lng is not None:
        msa_cities.append((lat, lng, row['CITY'], row['STATE']))

msa_heat_data = []
non_msa_heat_data = []

for index, row in locations_df.iterrows():
    address = row['ADDRESS']
    lat, lng = geocode_address(address)
    if lat is not None and lng is not None:
        within_msa = False
        for msa_lat, msa_lng, _, _ in msa_cities:
            distance = geodesic((lat, lng), (msa_lat, msa_lng)).miles
            if distance <= 50:
                msa_heat_data.append([lat, lng])
                within_msa = True
                break
        if not within_msa:
            non_msa_heat_data.append([lat, lng])

map_center = [39.8283, -98.5795]  # Note this is the center of the USA, for other regions you will have to update the center grids
heat_map = folium.Map(location=map_center, zoom_start=5)

#You can adjust the granularity and color seelction of your heat map here
if non_msa_heat_data:
    HeatMap(non_msa_heat_data, min_opacity=0.3, max_zoom=15, radius=25, blur=15, gradient={0.0: 'green', 1: 'green'}).add_to(heat_map)

if msa_heat_data:
    HeatMap(msa_heat_data, min_opacity=0.3, max_zoom=15, radius=25, blur=15, gradient={0.0: 'red', 1: 'red'}).add_to(heat_map)

heat_map.save('heatmap.html')
print("Heat map has been created and saved as heatmap.html")
