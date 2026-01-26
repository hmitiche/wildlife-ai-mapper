"""
'extract.py'
Extract GPS data from field observation images
and store in CSV file
author: Dr. Hakim Mitiche
update: Jan. 2026
"""
import os
import csv
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# -------- SETTINGS --------
INSECTA_IMAGE_FOLDER = "images_insects"          # Folder with pictures
FLORA_IMAGE_FOLDER = "images_flora"
FUNGUS_IMAGES_FOLDER = "images_fungus"
INSECTA_OUTPUT_CSV = "insecta_metadata.csv"
FLORA_OUTPUT_CSV = "flora_metadata.csv"
ORANGE = "\033[33m"
RESET = "\033[0m"
WARNING_ICON = "⚠️"


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


def already_processed_images(output_csv):
    # find already processed images (in output_csv file)
    processed_images = set()
    # check in the images metadata collection CSV file
    file_exists = os.path.exists(output_csv)
    if file_exists:
        with open(output_csv, newline="", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_images.add(row["picture_name"])

    print(f"[info] Already processed images: {len(processed_images)}")
    return processed_images

def collect_images_gps(images_folder, processed_images):
    # browse new images and collect GPS data
    rows = []
    gps_count = 0
    for file_name in os.listdir(images_folder):
        
        # skip files other then pictures
        if not file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            print(f"{ORANGE}{WARNING_ICON}Skipping not supported file: '{file_name}'{RESET}")
            continue

        # skip previously handled pictures
        if file_name in processed_images:
            print("[info] Skipping old image: ", file_name)
            continue

        # handle new images    
        print("[info] Processing: ", file_name, " ...")
        file_path = os.path.join(images_folder, file_name)

        try:
            img = Image.open(file_path)
            exif_data = get_exif_data(img)
            gps_data = get_gps_data(exif_data)
            img.close()

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
                    gps_count += 1
                else:
                    print(f"{ORANGE}{WARNING_ICON} Missing GPS coordinates in: {file_name}{RESET}")

                alt = gps_data.get("GPSAltitude")
                alt_ref = gps_data.get("GPSAltitudeRef", 0)

                if alt is not None:
                    altitude = round(to_float(alt), 2)
                    if alt_ref == 1:
                        altitude = -altitude
                else:
                    print(f"{ORANGE}{WARNING_ICON} Missing altitude in: {file_name}{RESET}")

            else:
                print(f"{ORANGE}{WARNING_ICON} No GPS metadata found in: {file_name}{RESET}")

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
            print(f"Skipping image '{file_name}'': {e}")
    print("[summary] Rows collected:", len(rows), " gps extracted: ", gps_count)
    return rows    

def write_output(output_csv, rows):
    """
    Save collected GPS data to CSV file
    """
    file_exists = os.path.exists(output_csv)
    with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
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
        print("[info] CSV file created: ", output_csv)
    else:
        print("[info] CSV file updated: ", output_csv)

def main():
    """
    main function
    """

    print("\n===== GPS METADATA EXTRACTION STARTED =====\n")

    # ---------- INSECTA ----------

    if os.path.exists(INSECTA_IMAGE_FOLDER):

        print(f"[info] Processing insect images...")
        print(f"{INSECTA_IMAGE_FOLDER}, files: ")
        total_images = len([
             f for f in os.listdir(INSECTA_IMAGE_FOLDER)
             if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])
        print(f"[info] Total insect images found: {total_images}")


        processed_insects = already_processed_images(INSECTA_OUTPUT_CSV)

        insect_rows = collect_images_gps(
            INSECTA_IMAGE_FOLDER,
            processed_insects
        )
        print(f"[summary] New insect images processed: {len(insect_rows)}")
        if insect_rows:
            write_output(INSECTA_OUTPUT_CSV, insect_rows)
        else:
            print("[info] No new insect images found!")

    else:
        print("[warning] Insect images folder not found.")


    # ---------- FLORA ----------

    if os.path.exists(FLORA_IMAGE_FOLDER):

        print("\n[info] Processing flora images...")
        total_images = len([
            f for f in os.listdir(FLORA_IMAGE_FOLDER)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])
        print(f"[info] Total flora images found: {total_images}")
        processed_flora = already_processed_images(FLORA_OUTPUT_CSV)

        flora_rows = collect_images_gps(
            FLORA_IMAGE_FOLDER,
            processed_flora
        )
        print(f"[summary] New flora images processed: {len(flora_rows)}")
        if flora_rows:
            write_output(FLORA_OUTPUT_CSV, flora_rows)
        else:
            print("[info] No new flora images found.")

    else:
        print("[warning] Flora image folder not found.")



    print("\n===== EXTRACTION FINISHED =====\n")

if __name__ == "__main__":
    main()
