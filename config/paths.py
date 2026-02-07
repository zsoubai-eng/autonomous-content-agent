import os

# Project Root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Departments
DEPARTMENTS_DIR = os.path.join(BASE_DIR, "departments")
INTELLIGENCE_DIR = os.path.join(DEPARTMENTS_DIR, "intelligence")
PRODUCTION_DIR = os.path.join(DEPARTMENTS_DIR, "production")
LOGISTICS_DIR = os.path.join(DEPARTMENTS_DIR, "logistics")

# Assets
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
SFX_DIR = os.path.join(ASSETS_DIR, "sfx")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

# Output
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SHORTS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "shorts")

# Temp
TEMP_DIR = os.path.join(BASE_DIR, "temp")
TEMP_THUMBNAILS_DIR = os.path.join(TEMP_DIR, "thumbnails")
TEMP_LOGS_DIR = os.path.join(TEMP_DIR, "logs")
TEMP_IMAGES_DIR = os.path.join(TEMP_DIR, "images")

# Ensure all directories exist
for directory in [
    MUSIC_DIR, SFX_DIR, FONTS_DIR, SHORTS_OUTPUT_DIR,
    TEMP_DIR, TEMP_THUMBNAILS_DIR, TEMP_LOGS_DIR, TEMP_IMAGES_DIR
]:
    os.makedirs(directory, exist_ok=True)
