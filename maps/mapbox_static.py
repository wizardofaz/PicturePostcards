# Fetch static map using Mapbox Static Maps API
import requests
from io import BytesIO
from PIL import Image

MAPBOX_STYLES = {
    "Streets": "mapbox/streets-v12",
    "Outdoors": "mapbox/outdoors-v12",
    "Light": "mapbox/light-v11",
    "Dark": "mapbox/dark-v11",
    "Satellite": "mapbox/satellite-v9",
    "Satellite Streets": "mapbox/satellite-streets-v12"
}

MAPBOX_TOKEN = "pk.eyJ1Ijoid2l6YXJkb2ZheiIsImEiOiJjbWNjdnRycDQwY2gyMm1wd3dhYzA2bWhzIn0.-LrnHWbpO3Eksp7H4IAXxg"

class MapboxStaticMap:
    def __init__(self, style="mapbox/streets-v12"):
        self.style = style if style in MAPBOX_STYLES.values() else "mapbox/streets-v12"

    def get_map_image(self, lat, lon, zoom=14, size=(300, 300)):
        width, height = size

        # Validate and format coordinates
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            raise ValueError("Latitude and Longitude must be float-compatible")

        url = (
            f"https://api.mapbox.com/styles/v1/{self.style}/static/"
            f"{lon},{lat},{zoom}/{width}x{height}"
            f"?access_token={MAPBOX_TOKEN}"
        )

        print("Requesting map from:", url)
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
