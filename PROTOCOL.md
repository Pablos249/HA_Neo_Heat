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

## Confirmed Circuit 1 write

A controlled proxy capture observed a 22-byte cloud-to-device command for
parameter `0x25`, with a float32 little-endian value and the same CRC algorithm.
Both `30 → 26` and `26 → 30` were followed by matching telemetry and settings
readback. The integration implements only this parameter and requires matching
settings readback before reporting success. The device identity bytes are
learned locally from validated frames and are never logged or published.

Other write parameters, full-frame writes, ranges and mode enumeration values
remain unverified and are not implemented.
