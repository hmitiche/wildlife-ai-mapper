
PHOTO GPS EXTRACTOR & MAP VIEWER
--------------------------------
author: Hakim Mitiche,
update: Jan 19th, 2026
--------------------------------

This tool extracts GPS and time metadata from photos and displays their locations on an interactive map.

REQUIREMENTS
------------
You need Python 3.8 or newer. To Install required libraries, open terminal and type:
	pip install pillow folium 

IMPORTANT NOTES
---------------
GPS must be enabled when photos are taken. WhatsApp and social media remove location data. Use original camera files. Map works offline after creation. 
COMMON PROBLEMS: 
	- No GPS data found.
	- Location was disabled when taking photos. 
	- Empty CSV file: Wrong images folder path. 
	- Photos contain no EXIF data. END OF FILE

FOLDER STRUCTURE
----------------
Your project folder must look like this:project/

---------
├── extract.py
├── map.py
├── images/
│   ├── IMG_001.jpg
│   ├── IMG_002.jpg
│   └── 

Folders
-------

images/ -> contains your observations as pictures with metadata included, 
		 can be: JPEG, JPG or PNG

scripts
-------

extract.py 
	Extracts metadata from photos and creates a CSV file.
	INPUT Folder:images/Supported image formats:JPGJPEGPNG (only if EXIF data exists)OUTPUT FILEphoto_metadata.csv
	CSV COLUMNS picture_name     -> Image file namedate             -> Capture date 
	(YYYY-MM-DD)hour             -> Capture time (HH:MM)note             -> Empty column for manual notesGPS coordinates  -> Latitude and longitude (DMS format)altitude         -> Elevation in meters

    HOW TO RUN
    Open Command Prompt or Terminal in the project folder, 
    type: 
    	python extract.py
    If successful you will see: CSV file created: 'photo_metadata.csvS'

 map.py
 	PURPOSE: Creates an interactive map from the CSV file.
 	INPUT FILE: 'photo_metadata.csv'
 	OUTPUT FILE: 'photo_map.html' 
 	HOW TO RUN: type:
 		python map.py
 	If successful you will seea map created: 'photo_map.html'
 	OPENING THE OUTPUT FILES:
 	OPEN CSV FILE
 		Option 1: Double-click:photo_metadata.csv(It will open in Excel or LibreOffice)
		Option 2: Upload to Google Sheets. OPEN MAP FILE, Double-click:photo_map.html
 		It will open in your web browser.
 		Features: Zoom in/outPan map. 
		Click markersView photo information

