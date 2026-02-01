"""Constants for Strasbourg Parkings integration."""

from datetime import timedelta

DOMAIN = "strasbourg_parkings"
CONF_PARKINGS = "parkings"

# API Configuration
API_BASE_URL = "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/occupation-parkings-temps-reel/records"
SCAN_INTERVAL = timedelta(minutes=3)
