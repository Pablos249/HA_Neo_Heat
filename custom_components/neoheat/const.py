"""Public constants; no device-specific configuration."""
DOMAIN = "neoheat"
DEFAULT_PORT = 502

# Observed telemetry values at byte offset 171. The values match the cloud
# mode codes multiplied by five for Stop, DHW and central heating.
OPERATING_MODES = {
    0: "Stop",
    5: "DHW",
    10: "Central heating",
}


def decode_operating_mode(value):
    """Translate the observed scaled operating mode; unknown codes stay unknown."""
    code = round(value)
    if abs(value - code) > 0.01:
        return None
    return OPERATING_MODES.get(code)

