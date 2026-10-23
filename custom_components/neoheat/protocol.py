"""Read-only decoder for observed Neoheat frames, independent of HA.

Offsets are empirical byte positions, NOT Modbus register addresses.
Device identity bytes are deliberately not exposed or logged.
"""
import math
import struct


def crc16(data: bytes) -> int:
    """CRC-16 reflected polynomial A001, initial value FFFF."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def decode_frame(frame: bytes) -> tuple[int, dict[int, float]]:
    if len(frame) < 15 or frame[:2] != b"\xaa\x55" or frame[-1] != 0x3A:
        raise ValueError("Invalid frame envelope")
    kind = frame[12]
    if (kind, len(frame)) not in ((1, 198), (2, 570)):
        raise ValueError("Unsupported frame layout")
    if int.from_bytes(frame[10:12], "little") + 15 != len(frame):
        raise ValueError("Invalid frame length")
    if crc16(frame[2:-3]) != int.from_bytes(frame[-3:-1], "little"):
        raise ValueError("Invalid frame checksum")
    start = 35 if kind == 1 else 15
    values = {}
    for offset in range(start, len(frame) - 3, 4):
        value = struct.unpack_from("<f", frame, offset)[0]
        if math.isfinite(value):
            values[offset] = value
    return kind, values


class FrameDecoder:
    """Handle fragmented/coalesced TCP chunks and recover from corrupt data."""

    def __init__(self):
        self.buffer = bytearray()

    def feed(self, chunk: bytes) -> list[tuple[int, dict[int, float]]]:
        self.buffer.extend(chunk)
        result = []
        while True:
            start = self.buffer.find(b"\xaa\x55")
            if start == -1:
                self.buffer[:] = self.buffer[-1:]
                break
            del self.buffer[:start]
            if len(self.buffer) < 13:
                break
            size = int.from_bytes(self.buffer[10:12], "little") + 15
            if (self.buffer[12], size) not in ((1, 198), (2, 570)):
                del self.buffer[:2]
                continue
            if len(self.buffer) < size:
                break
            try:
                frame = decode_frame(bytes(self.buffer[:size]))
            except ValueError:
                del self.buffer[:2]
                continue
            result.append(frame)
            del self.buffer[:size]
        return result

