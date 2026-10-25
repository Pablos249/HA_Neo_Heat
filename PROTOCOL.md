# Observed protocol (experimental)

This describes observations, not a manufacturer specification.

| Position | Meaning |
| --- | --- |
| 0–1 | AA 55 start marker |
| 2–9 | Opaque header, deliberately not published from real captures |
| 10–11 | Little-endian size field; total length = field + 15 |
| 12 | Observed type: 1 telemetry, 2 settings |
| 13–14 | Opaque bytes |
| 15 onward | Payload (not all fields understood) |
| last 3, last 2 | CRC16 little-endian |
| last byte | 3A terminator |

CRC uses reflected polynomial 0xA001 and initial value 0xFFFF over bytes
2 through length-4 inclusive. This matched all 12 frames in two local captures,
including both observed types. It is a corruption check, not authentication.

Telemetry has total length 198; the exported float32 little-endian fields begin
at byte 35. Settings have length 570 with float32 fields beginning at byte 15.
Unknown types are discarded. Decoder resynchronizes after invalid data and
does not publish non-finite floats. Definitions in `sensor.py` are offsets
within frames, not Modbus addresses. Similar or equal observed values cannot
prove that two fields have been distinguished correctly.

## Write commands

A proxy capture showed a 22-byte cloud-to-device command containing parameter
`0x25` and a float32 little-endian value. Replaying an isolated command locally
can stop both local and cloud communication until the heat pump is restarted.
The capture does not reveal the required session, sequencing or bus-arbitration
rules, so a matching checksum and payload are not sufficient for safe control.

This integration is read-only and does not generate or transmit write commands.

## Operating mode

Across observed stop, DHW and central-heating samples, telemetry byte offset
171 held `0`, `5` and `10`, respectively. These values match cloud mode codes
`0`, `1` and `2` multiplied by five. The integration exposes a read-only enum
for these three values. Other values remain unknown; this mapping is empirical
for the observed EKO II 15 and has not been verified against a manufacturer
specification or other models.
