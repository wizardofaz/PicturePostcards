# Combines photo, map, and annotations into final image
from PIL import Image, ImageDraw, ImageFont
from maps.mapbox_static import MapboxStaticMap

def create_postcard_image(photo_path, metadata):
    base = Image.new("RGB", (800, 600), "white")
    photo = Image.open(photo_path)
    photo.thumbnail((400, 300), Image.Resampling.LANCZOS)
    base.paste(photo, (50, 50))

    # Insert map if GPS is available
    if "Latitude" in metadata and "Longitude" in metadata:
        lat, lon = metadata["Latitude"], metadata["Longitude"]
        style = metadata.get("MapboxStyle", "streets")
        zoom = metadata.get("MapZoom", 14)
        map_image = MapboxStaticMap(style=style).get_map_image(lat, lon, zoom=zoom, size=(300, 300))
        base.paste(map_image, (500, 50))
    else:
        draw = ImageDraw.Draw(base)
        font = ImageFont.load_default()
        draw.text((500, 50), "No GPS for map", fill="gray", font=font)

    draw = ImageDraw.Draw(base)
    font = ImageFont.load_default()
    y = 370
    for k, v in metadata.items():
        if k not in ("GPSInfo", "MapboxStyle", "MapZoom"):
            draw.text((50, y), f"{k}: {v}", fill="black", font=font)
            y += 20

    return base

def create_postcard(photo_path, metadata, output_path):
    img = create_postcard_image(photo_path, metadata)
    img.save(output_path)
