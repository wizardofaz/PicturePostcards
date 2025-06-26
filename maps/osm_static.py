# Fetch map using OpenStreetMap tile server
import requests
from PIL import Image
from io import BytesIO

from maps.provider import MapProvider

class OSMStaticMap(MapProvider):
    def get_map_image(self, lat, lon, zoom=14, size=(300, 300)):
        width, height = size
        url = (
            f"https://staticmap.openstreetmap.de/staticmap.php"
            f"?center={lat},{lon}&zoom={zoom}&size={width}x{height}&markers={lat},{lon},red"
        )
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
