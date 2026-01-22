"""
'extract.py'
author: Dr. Hakim Mitiche
update: Jan. 2026
"""
import os
import csv
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# -------- SETTINGS --------
IMAGE_FOLDER = "images"          # Folder with pictures
OUTPUT_CSV = "photo_metadata.csv"

# -------- HELPER FUNCTIONS --------
def to_float(x):
    """Safely convert EXIF numbers (IFDRational, tuple, int, float) to float."""
    try:
        return float(x)
    except TypeError:
        return float(x[0]) / float(x[1])


def get_exif_data(image):
    exif_data = {}
    info = image._getexif()
    if info is None:
        return exif_data

    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        exif_data[decoded] = value
    return exif_data


def get_gps_data(exif_data):
    gps_info = {}
    gps_data = exif_data.get("GPSInfo")

    if gps_data is None:
        return None

    for key in gps_data:
        decoded = GPSTAGS.get(key, key)
        gps_info[decoded] = gps_data[key]

    return gps_info


def dms_to_decimal(dms, ref):
    def to_float(x):
        return float(x)

    degrees = to_float(dms[0])
    minutes = to_float(dms[1])
    seconds = to_float(dms[2])

    decimal = degrees + minutes / 60 + seconds / 3600

    if ref in ["S", "W"]:
        decimal *= -1

    return decimal


def dms_string(dms, ref):
    d = int(float(dms[0]))
    m = int(float(dms[1]))
    s = round(float(dms[2]), 2)

    return f"{d}°{m}'{s}\" {ref}"



# -------- MAIN PROCESS --------

# find already processed images (in OUTPUT_CSV file)
processed_images = set()

# check in the images metadata collection CSV file
file_exists = os.path.exists(OUTPUT_CSV)
if file_exists:
    with open(OUTPUT_CSV, newline="", mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed_images.add(row["picture_name"])

print(f"[info] Already processed images: {len(processed_images)}")

rows = []

# browse new images and collect GPS data
for file_name in os.listdir(IMAGE_FOLDER):
    
    # skip files other then pictures
    if not file_name.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    # skip previously handled pictures
    if file_name in processed_images:
        print("[info] Skipping old image: ", file_name)
        continue

    # handle new images    
    print("[info] Processing: ", file_name, " ...")
    file_path = os.path.join(IMAGE_FOLDER, file_name)

    try:
        img = Image.open(file_path)
        exif_data = get_exif_data(img)
        gps_data = get_gps_data(exif_data)

        # Default values
        latitude_dms = ""
        longitude_dms = ""
        altitude = ""
        date = ""
        hour = ""

        # --- Date & Time ---
        datetime = exif_data.get("DateTime", "")
        if datetime:
            parts = datetime.split(" ")
            date = parts[0].replace(":", "-")
            hour = parts[1]

        # --- GPS ---
        if gps_data:
            lat = gps_data.get("GPSLatitude")
            lat_ref = gps_data.get("GPSLatitudeRef")
            lon = gps_data.get("GPSLongitude")
            lon_ref = gps_data.get("GPSLongitudeRef")

            if lat and lon:
                latitude_dms = dms_string(lat, lat_ref)
                longitude_dms = dms_string(lon, lon_ref)

            alt = gps_data.get("GPSAltitude")
            alt_ref = gps_data.get("GPSAltitudeRef", 0)

            if alt is not None:
                altitude = round(to_float(alt),2)
                if alt_ref == 1:
                    altitude = -altitude


        gps_string = f"{latitude_dms}, {longitude_dms}"
        # for debugging
        #print("[info] file_name, type(lat), lat)

        rows.append([
            file_name,
            date,
            hour,
            "",                  # note column left empty
            gps_string,
            altitude
        ])

    except Exception as e:
        print(f"Skipping {file_name}: {e}")


# -------- WRITE CSV --------

with open(OUTPUT_CSV, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # write cvs header (columns labels) only if the file is new
    if not file_exists:
        writer.writerow([
            "picture_name",
            "date",
            "hour",
            "note",
            "GPS coordinates (DMS)",
            "altitude"
        ])

    writer.writerows(rows)

if not file_exists:
    print("[info] CSV file created:", OUTPUT_CSV)
else:
    print("[info] CSV file updated:", OUTPUT_CSV)