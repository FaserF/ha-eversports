# custom_components/eversports/const.py
"""Constants for the Eversports integration."""
from datetime import timedelta
import logging

DOMAIN = "eversports"
LOGGER = logging.getLogger(__package__)

# Platforms
PLATFORMS = ["sensor"]

# Configuration and options
CONF_FACILITY_ID = "facility_id"
CONF_SPORT = "sport"
CONF_COURT_IDS = "court_ids"

# Update interval
UPDATE_INTERVAL = timedelta(minutes=15)

# API
BASE_URL = "https://www.eversports.de/widget/api/slot"