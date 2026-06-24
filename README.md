# Eversports Home Assistant Integration 🎾

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Downloads (Current release)](https://img.shields.io/github/downloads/FaserF/ha-eversports/latest/eversports.zip?label=Downloads%20(Current%20release)&style=for-the-badge)](https://github.com/FaserF/ha-eversports/releases)
[![Tests](https://github.com/FaserF/ha-eversports/actions/workflows/tests.yaml/badge.svg)](https://github.com/FaserF/ha-eversports/actions/workflows/tests.yaml)

Track court availability from **Eversports** directly in Home Assistant.

---

## ❤️ Support This Project

> I maintain this integration in my **free time alongside my regular job** — bug hunting, new features, and testing on real hardware. Test devices cost money, and every donation helps me stay independent and free up more time for open-source work.
>
> Donations are completely voluntary — but the more support I receive, the less I depend on other income sources and the more time I can realistically invest into these GitHub projects. 💪

<div align="center">

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor%20on-GitHub-%23EA4AAA?style=for-the-badge&logo=github-sponsors&logoColor=white)](https://github.com/sponsors/FaserF)&nbsp;&nbsp;
[![PayPal](https://img.shields.io/badge/Donate%20via-PayPal-%2300457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/FaserF)

</div>

---
## Features ✨

- **Availability Monitoring**: Check free slots for specific sports and facilities.
- **Detailed Attributes**: Get next slot time, available count, and more.
- **Calendar Integration**: View all available slots directly in your calendar.
- **Binary Sensor**: Simple "Yes/No" sensor for available slots.
- **Health Checks**: Automatic Home Assistant Repair notification if data cannot be fetched for 24 hours (e.g., due to API or website changes).
- **Easy Configuration**: Simple setup via the Home Assistant UI.

## Installation 🛠️

### Using HACS (Recommended)

1. Open **HACS** in your Home Assistant instance.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add `https://github.com/FaserF/ha-eversports` with category **Integration**.
4. Search for **Eversports** and click **Download**.
5. Restart Home Assistant.

### Manual Installation

1. Download the latest [Release](https://github.com/FaserF/ha-eversports/releases/latest).
2. Extract the ZIP file.
3. Copy the `custom_components/eversports` folder to your `<config_dir>/custom_components/` directory.
4. Restart Home Assistant.

## Configuration ⚙️

1. Go to **Settings** -> **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Eversports**.
4. Follow the configuration steps providing your Facility ID, Sport, and Court IDs.

### Finding Required IDs

1. Visit the booking page of your facility on Eversports.
2. Open your browser's Developer Tools (F12) and go to the **Network** tab.
3. Refresh the page and look for a request starting with `https://www.eversports.de/widget/api/slot?`.
4. The URL contains the `facilityId`, `sport`, and `courts[]` parameters you need.

## Automation Examples 🤖

Here are some examples of how you can use the Eversports sensors in your Home Assistant automations.

<details>
<summary><b>1. Persistent Notification when a slot becomes available</b></summary>

This automation sends a notification to the Home Assistant frontend whenever a new slot is found.

```yaml
alias: "Eversports: Notify available slot"
trigger:
  - platform: state
    entity_id: sensor.eversports_squash_next_available
condition:
  - condition: not
    conditions:
      - condition: state
        entity_id: sensor.eversports_squash_next_available
        state: "Keine freien Slots"
action:
  - service: notify.persistent_notification
    data:
      title: "Squash Slot Available! 🎾"
      message: >
        A slot is available at {{ states('sensor.eversports_squash_next_available') }}.
        Total free slots today: {{ state_attr('sensor.eversports_squash_next_available', 'available_slots_count') }}
```
</details>

<details>
<summary><b>2. Mobile Notification (App/Telegram) with details</b></summary>

Get a push notification on your phone with the exact time and a list of all available slots.

```yaml
alias: "Eversports: Mobile Alert"
trigger:
  - platform: state
    entity_id: sensor.eversports_squash_next_available
condition:
  - condition: not
    conditions:
      - condition: state
        entity_id: sensor.eversports_squash_next_available
        state: "Keine freien Slots"
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "Eversports Squash"
      message: >
        Next free slot: {{ states('sensor.eversports_squash_next_available') }}
        All times: {{ state_attr('sensor.eversports_squash_next_available', 'available_slots_list') | join(', ') }}
      data:
        clickAction: "https://www.eversports.de/s/{{ state_attr('sensor.eversports_squash_next_available', 'facility_id') }}"
```
</details>

<details>
<summary><b>3. Custom Markdown Card for Dashboard</b></summary>

Use this template in a manual **Markdown Card** to get a beautiful overview of available times.

```text
### Eversports Squash 🎾
{% set state = states('sensor.eversports_squash_next_available') %}
{% if state != 'Keine freien Slots' %}
**Next Slot:** {{ state }}
**Free today:** {{ state_attr('sensor.eversports_squash_next_available', 'available_slots_count') }}

**Available Times:**
{% for time in state_attr('sensor.eversports_squash_next_available', 'available_slots_list') %}
- {{ time }}
{% endfor %}

[Book now](https://www.eversports.de/s/{{ state_attr('sensor.eversports_squash_next_available', 'facility_id') }})
{% else %}
*Currently no slots available for today.*
{% endif %}
```
</details>

<details>
<summary><b>4. Alert if integration stops working (24h failure)</b></summary>

Since we implemented a repair issue, you can also monitor the "last update" attribute to get an early warning.

```yaml
alias: "Eversports: API Failure Alert"
trigger:
  - platform: template
    value_template: >
      {{ (now() - as_datetime(state_attr('sensor.eversports_squash_next_available', 'last_update'))).total_seconds() > 86400 }}
action:
  - service: notify.persistent_notification
    data:
      title: "Eversports Timeout"
      message: "The Eversports integration hasn't updated for 24 hours. Check the Repairs section!"
```
</details>

## Troubleshooting 🔍

If you see a Home Assistant Repair issue, it means the integration hasn't been able to fetch data for 24 hours. This usually happens if Eversports changes their website structure. Please check for updates or [open an issue](https://github.com/FaserF/ha-eversports/issues).

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.eversports: debug
```

## Support

If you like this integration, feel free to give it a star on GitHub! ⭐
Documentation is mostly based on the community's effort. Contributions are welcome.