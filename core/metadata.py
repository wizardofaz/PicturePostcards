# Handles EXIF parsing and manual metadata input
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_metadata(image_path):
    img = Image.open(image_path)
    exif_data = img._getexif() or {}
    metadata = {}

    def rational_to_float(val):
        try:
            return val[0] / val[1] if isinstance(val, tuple) else float(val)
        except Exception:
            return float(val)

    def dms_to_decimal(dms, ref):
        try:
            degrees = rational_to_float(dms[0])
            minutes = rational_to_float(dms[1])
            seconds = rational_to_float(dms[2])
            decimal = degrees + minutes / 60 + seconds / 3600
            if ref in ['S', 'W']:
                decimal = -decimal
            return decimal
        except Exception as e:
            print(f"Error converting DMS to decimal: {e}")
            return None

    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            gps_data = {}
            for t in value:
                gps_tag = GPSTAGS.get(t, t)
                gps_data[gps_tag] = value[t]
            metadata["GPSInfo"] = gps_data
            try:
                lat = dms_to_decimal(gps_data["GPSLatitude"], gps_data["GPSLatitudeRef"])
                lon = dms_to_decimal(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])
                if lat is not None and lon is not None:
                    metadata["Latitude"] = lat
                    metadata["Longitude"] = lon
            except Exception:
                pass
        elif tag in ["DateTime", "Model"]:
            metadata[tag] = value

    return metadata
