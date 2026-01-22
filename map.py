"""
'map.py'
author: Dr. Hakim Mitiche
update: Jan. 2026
"""
import csv
import folium
import re
import os

CSV_FILE = "photo_metadata.csv"
IMAGE_FOLDER = "images"
OUTPUT_MAP = "photo_map.html"

# --- DMS to decimal ---
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

# --- Main program ---
# make sure there are geo data
if not os.path.isfile(CSV_FILE):
    print(f"[ERROR] Observations CVS file not found: '{os.path.abspath(CSV_FILE)}'")
    print(f"Make sure there are valid images in '{IMAGE_FOLDER}/' folder and 'extract.py' was run and ve created the CSV file!")
    sys.exit(1) 
# --- Load CSV ---
locations = []

with open(CSV_FILE, newline="", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    i = 0
    for row in reader:
        gps = row["GPS coordinates (DMS)"].replace('""','"')
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
                "date": row["date"],
                "hour": row["hour"],
                "alt": row["altitude"],
                "note": row.get("note","")
            })
        except Exception as e:
            print(f"Skipping row {i}:", e)
        i+=1

# --- Create map ---
center_lat = locations[0]["lat"] if locations else 0
center_lon = locations[0]["lon"] if locations else 0
m = folium.Map(location=[center_lat, center_lon], zoom_start=17)

# --- Add markers ---
for loc in locations:
    image_file = os.path.join(IMAGE_FOLDER, loc['name'])
    if os.path.exists(image_file):
        # Use relative path; HTML object ensures unique iframe per marker
        image_html = f'<a href="{image_file}" target="_blank">' \
                     f'<img src="{image_file}" width="150"></a>'
    else:
        image_html = "Image not found"

    html_content = f"""
    <b>{loc['name']}</b><br>
    Date: {loc['date']}<br>
    Time: {loc['hour']}<br>
    Latitude: {loc['lat']:.6f}<br>
    Longitude: {loc['lon']:.6f}<br>
    Altitude: {loc['alt']} m<br>
    Note: {loc['note']}<br>
    {image_html}
    """

    # --- Use folium.Html to ensure unique iframe per popup ---
    from folium import Html, Popup
    popup = Popup(Html(html_content, script=True), max_width=265)

    folium.Marker(
        location=[loc["lat"], loc["lon"]],
        popup=popup,
        tooltip=loc["name"]
    ).add_to(m)

# --- Save map ---
m.save(OUTPUT_MAP)
print("[info] Map created: '", OUTPUT_MAP,"'")