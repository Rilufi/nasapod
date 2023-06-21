import json
import urllib.request
import geopandas as gpd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# Fetching ISS info
url = "http://api.open-notify.org/iss-now.json"
response = urllib.request.urlopen(url)
result = json.loads(response.read())
location = result["iss_position"]
latitude = float(location['latitude'])
longitude = float(location['longitude'])
geolocator = Nominatim(user_agent="geoapiExercises")
coordinates = (latitude, longitude)
location = geolocator.reverse(coordinates, exactly_one=True)

if location is not None and location.raw.get("address") is not None:
    address = location.raw["address"]
    country = address.get("country")
    print("País: ", country)
else:
    print("Não foi possível determinar a localização.")

# Creating the world map
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Plotting the world map
fig, ax = plt.subplots(figsize=(10, 6))
world.plot(ax=ax)#, color='lightgray')

# Plotting the ISS location
ax.plot(longitude, latitude, 'ro', markersize=6)

# Saving the map as PNG
plt.savefig('iss_map.png', dpi=300, bbox_inches='tight')
