"""Constants for Strasbourg Parkings integration."""
from datetime import timedelta

DOMAIN = "strasbourg_parkings"
CONF_PARKINGS = "parkings"

# API Configuration
API_BASE_URL = "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/occupation-parkings-temps-reel/records"
SCAN_INTERVAL = timedelta(minutes=3)  # 3 minutes (données rafraîchies toutes les 3 minutes)

# Mapping between user-friendly IDs and API idsurfs values
PARKINGS_API_IDS = {
    "AUSTERLITZ": "1375_DEP_1",
    "BATELIERS": "1377_DEP_3",
    "BROGLIE": "1378_DEP_4",
    "ESPLANADE": "1703_DEP_27",
    "GARE": "1382_DEP_8",
    "GUTENBERG": "1383_DEP_9",
    "KLEBER": "1388_DEP_14",
    "P1HALLES": "1384_DEP_10",
    "P2HALLES": "1385_DEP_11",
    "P3HALLES": "1386_DEP_12",
    "PETITE_FRANCE": "1390_DEP_16",
    "RIVETOILE": "1392_DEP_18",
    "STE_AURELIE": "1396_DEP_22",
    "STNICHOLAS": "1395_DEP_21",
}

# Liste complète des parkings de Strasbourg avec leurs noms affichés
PARKINGS_LIST = {
    "AUSTERLITZ": "Austerlitz",
    "BATELIERS": "Bateliers",
    "BROGLIE": "Opéra Broglie",
    "ESPLANADE": "Esplanade",
    "GARE": "Gare Wodli",
    "GUTENBERG": "Gutenberg",
    "KLEBER": "Kléber Homme de Fer",
    "P1HALLES": "Halles P1 Marais Vert",
    "P2HALLES": "Halles P2 Sébastopol",
    "P3HALLES": "Halles P3 Wilson",
    "PETITE_FRANCE": "Centre Historique Petite France",
    "RIVETOILE": "Rivétoile",
    "STE_AURELIE": "Sainte-Aurélie Gare",
    "STNICHOLAS": "Saint-Nicolas",
}
