"""Configure an explicitly supplied local endpoint."""
import voluptuous as vol
from homeassistant import config_entries
from .client import NeoheatClient
from .const import DEFAULT_PORT, DOMAIN


class NeoheatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self._form("user", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._form("reconfigure", user_input)

    async def _form(self, step, user_input):
        errors = {}
        current = self._get_reconfigure_entry() if step == "reconfigure" else None
        if user_input is not None:
            user_input = {"host": user_input["host"].strip().lower(), "port": user_input["port"]}
            if not user_input["host"] or "://" in user_input["host"] or "/" in user_input["host"]:
                errors["base"] = "invalid_host"
            elif any(e.entry_id != (current.entry_id if current else None)
                     and e.data == user_input for e in self._async_current_entries()):
                return self.async_abort(reason="already_configured")
            else:
                client = NeoheatClient(user_input["host"], user_input["port"])
                try:
                    await client.read_snapshot()
                except (OSError, TimeoutError):
                    errors["base"] = "cannot_connect"
                else:
                    if current:
                        return self.async_update_reload_and_abort(current, data_updates=user_input)
                    return self.async_create_entry(title="Neoheat", data=user_input)
                finally:
                    await client.close()
        defaults = user_input or (current.data if current else {})
        return self.async_show_form(step_id=step, errors=errors, data_schema=vol.Schema({
            vol.Required("host", default=defaults.get("host", "")): str,
            vol.Required("port", default=defaults.get("port", DEFAULT_PORT)):
                vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
        }))

