"""
'map.py'
author: Dr. Hakim Mitiche
update: Jan. 2026
"""

import csv
import folium
import re
import os
import sys

# ---------------- CONFIG ----------------

INSECTA_CSV = "insecta_metadata.csv"
FLORA_CSV = "flora_metadata.csv"

INSECTA_FOLDER = "images_insects"
FLORA_FOLDER = "images_flora"

OUTPUT_MAP = "bio_observations_map.html"

# ---------------- DMS to Decimal ----------------

def dms_to_decimal(dms_string):
    pattern = r"(\d+)°(\d+)'([\d\.]+)\"? ([NSEW])"
    match = re.match(pattern, dms_string.strip())
    if not match:
        return None

    deg, minutes, seconds, ref = match.groups()
    decimal = float(deg) + float(minutes)/60 + float(seconds)/3600

    if ref in ["S", "W"]:
        decimal *= -1

    return decimal


# ---------------- CSV Loader ----------------

def load_locations(csv_file, image_folder, category):
    locations = []

    if not os.path.isfile(csv_file):
        print(f"[warning] Missing file: {csv_file}")
        return locations

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):

            gps = row.get("GPS coordinates (DMS)", "").replace('""','"')

            if not gps:
                continue

            try:
                lat_dms, lon_dms = gps.split(",")

                lat = dms_to_decimal(lat_dms.strip())
                lon = dms_to_decimal(lon_dms.strip())

                if lat is None or lon is None:
                    continue

                locations.append({
                    "lat": lat,
                    "lon": lon,
                    "name": row["picture_name"],
                    "date": row.get("date",""),
                    "hour": row.get("hour",""),
                    "alt": row.get("altitude",""),
                    "note": row.get("note",""),
                    "folder": image_folder,
                    "type": category
                })

            except Exception as e:
                print(f"[warning] Skipping row {i} in {csv_file}: {e}")

    print(f"[info] Loaded {len(locations)} {category} points")
    return locations


# ---------------- MAIN ----------------

print("[info] Loading datasets...")

insecta_points = load_locations(INSECTA_CSV, INSECTA_FOLDER, "Insect")
flora_points = load_locations(FLORA_CSV, FLORA_FOLDER, "Flora")

all_locations = insecta_points + flora_points

if not all_locations:
    print("[ERROR] No valid GPS points found.")
    sys.exit(1)

# ---------------- Create Map ----------------

center_lat = all_locations[0]["lat"]
center_lon = all_locations[0]["lon"]

m = folium.Map(location=[center_lat, center_lon], zoom_start=17)

# ---------------- Add Markers ----------------

for loc in all_locations:

    image_path = os.path.join(loc["folder"], loc["name"])

    if os.path.exists(image_path):
        image_html = f'''
        <a href="{image_path}" target="_blank">
        <img src="{image_path}" width="160">
        </a>
        '''
    else:
        image_html = "<i>Image not found</i>"

    html_content = f"""
    <b>{loc['name']}</b><br>
    Type: {loc['type']}<br>
    Date: {loc['date']}<br>
    Time: {loc['hour']}<br>
    Latitude: {loc['lat']:.6f}<br>
    Longitude: {loc['lon']:.6f}<br>
    Altitude: {loc['alt']} m<br>
    Note: {loc['note']}<br>
    {image_html}
    """

    from folium import Html, Popup

    popup = Popup(Html(html_content, script=True), max_width=280)

    # Marker styling
    if loc["type"] == "Insect":
        icon = folium.Icon(color="red", icon="bug", prefix="fa")
    else:
        icon = folium.Icon(color="green", icon="leaf", prefix="fa")

    folium.Marker(
        location=[loc["lat"], loc["lon"]],
        popup=popup,
        tooltip=f"{loc['type']} — {loc['name']}",
        icon=icon
    ).add_to(m)

# ---------------- Save Map ----------------

m.save(OUTPUT_MAP)

print("[info] Map created successfully:")
print(" ->", OUTPUT_MAP)
print("[info] to check the map: \n\t python lauch.py")
