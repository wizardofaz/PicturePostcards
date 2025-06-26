# Map provider base class

class MapProvider:
    def get_map_image(self, lat, lon, zoom=14, size=(300, 300)):
        raise NotImplementedError("MapProvider subclasses must implement get_map_image()")
