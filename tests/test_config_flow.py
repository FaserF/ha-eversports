"""Test Eversports config flow."""

from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.eversports.const import DOMAIN
from .const import MOCK_CONFIG


async def test_user_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.eversports.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            MOCK_CONFIG,
        )
        await hass.async_block_till_done()

    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["title"] == f"Eversports {MOCK_CONFIG['sport'].capitalize()}"
    assert result2["data"] == MOCK_CONFIG
    assert len(mock_setup_entry.mock_calls) == 1
