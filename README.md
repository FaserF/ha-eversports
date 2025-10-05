[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
# eversports Homeassistant Sensor
This integration adds a sensor to Home Assistant to monitor the availability of sports courts from Eversports. It fetches data for a specific facility, sport, and a list of courts, and shows the next available time slot for the current day.

## Installation
### 1. Using HACS (recommended way)

This integration will be a official HACS Integration in the future.

Open HACS then install the "eversports" integration or use the link below.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FaserF&repository=ha-eversports&category=integration)

If you use this method, your component will always update to the latest version.

### 2. Manual

- Download the latest zip release from [here](https://github.com/FaserF/ha-eversports/releases/latest)
- Extract the zip file
- Copy the folder "eversports" from within custom_components with all of its components to `<config>/custom_components/`

where `<config>` is your Home Assistant configuration directory.

>__NOTE__: Do not download the file by using the link above directly, the status in the "master" branch can be in development and therefore is maybe not working.

## Configuration

Go to Configuration -> Integrations and click on "add integration". Then search for "eversports".

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=eversports)

### Configuration Variables
#### How to find the required IDs
Since these values are specific to each sports facility and sport, you need to find them manually using your browser's developer tools.

1. Navigate to the booking page of your desired sports facility that uses the Eversports widget.
2. Open the Developer Tools in your browser (usually by pressing F12).
3. Go to the Network tab. You might need to refresh the page.
4. On the website, select a date to view the court schedule. This will trigger an API request.
5. In the Network tab, look for a request URL that starts with https://www.eversports.de/widget/api/slot?.... You can use the filter bar and search for slot.
6. Click on this request to see the details. The "Request URL" will contain all the information you need.

Example URL: https://www.eversports.de/widget/api/slot?facilityId=24105&sport=squash&startDate=2025-10-05&courts[]=52463&courts[]=52464

#### Configurable settings
- **facility_id**: Your facility ID from the URL
- **sport name**: The sport name to be tracked (f.e. squash or pickleball) (from the URL)
- **court IDs**:  Your court IDs from the URL (enter these as a comma-separated list in the configuration).

## Sensors
The integration will create one sensor for each configured Eversports instance.

sensor.eversports_{sport}_next_available
State: The start time of the next available slot for the current day (e.g., 17:30). If no slots are available, the state will be Keine freien Slots.

Attributes:
- next_slot_datetime: Full timestamp of the next available slot in ISO format.
- next_slot_court_id: The ID of the court for the next available slot.
- available_slots_count: Total number of available slots for the rest of the day.
- available_slots_list: A list of all available start times for today.
- total_slots_count: The total number of slots (both available and booked) for the day.
- facility_id: The configured Facility ID.
- sport: The configured sport name.
- monitored_courts: A list of the court IDs you are monitoring.
- last_update: Timestamp of the last successful data fetch.

## Accessing the data

### Custom sensor
Add a custom sensor in your configuration.yaml

```yaml
{% set next_slot = states('sensor.eversports_squash_next_available') %}
  {% if next_slot != 'Keine freien Slots' %}
    Next free slot: **{{ next_slot }} o'clock**

    Number of free slots today: **{{ state_attr('sensor.eversports_squash_next_available', 'available_slots_count') }}**

    Further dates: {{ state_attr('sensor.eversports_squash_next_available', 'available_slots_list') | join(', ') }}
  {% else %}
    Unfortunately, there are no more slots available today.
  {% endif %}
```

## Bug reporting
Open an issue over at [github issues](https://github.com/FaserF/ha-eversports/issues). Please prefer sending over a log with debugging enabled.

To enable debugging enter the following in your configuration.yaml

```yaml
logger:
    logs:
        custom_components.eversports: debug
```

You can then find the log in the HA settings -> System -> Logs -> Enter "eversports" in the search bar -> "Load full logs"

## Thanks to
Huge thanks to [eversports.de](https://www.eversports.de/) for their API, meant for widgets!

The data is coming from the corresponding [eversports.de](https://www.eversports.de/) website.