"""Synthetic fixtures only: no identifiers or packets from a real home."""
import asyncio
import importlib.util
from pathlib import Path
import struct
import sys
import types
import unittest

BASE = Path(__file__).resolve().parents[1] / "custom_components" / "neoheat"
package = types.ModuleType("neoheat_test")
package.__path__ = [str(BASE)]
sys.modules["neoheat_test"] = package


def load(name):
    spec = importlib.util.spec_from_file_location(f"neoheat_test.{name}", BASE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


protocol = load("protocol")
client = load("client")


def packet(kind=1, values=None):
    size = 198 if kind == 1 else 570
    frame = bytearray(size)
    frame[:2] = b"\xaa\x55"
    frame[10:12] = (size - 15).to_bytes(2, "little")
    frame[12] = kind
    for offset, value in (values or {}).items():
        struct.pack_into("<f", frame, offset, value)
    frame[-3:-1] = protocol.crc16(frame[2:-3]).to_bytes(2, "little")
    frame[-1] = 0x3A
    return bytes(frame)


class ProtocolTests(unittest.TestCase):
    def test_known_crc_check_vector(self):
        self.assertEqual(protocol.crc16(b"123456789"), 0x4B37)

    def test_values_and_negative_temperature(self):
        kind, fields = protocol.decode_frame(packet(values={115: -12.5, 99: 42}))
        self.assertEqual(kind, 1)
        self.assertEqual(fields[115], -12.5)
        self.assertEqual(fields[99], 42)

    def test_settings(self):
        kind, fields = protocol.decode_frame(packet(2, {163: 30, 231: 45}))
        self.assertEqual((kind, fields[231]), (2, 45))

    def test_nonfinite_not_exported(self):
        _, fields = protocol.decode_frame(packet(values={35: float('nan'), 39: float('inf')}))
        self.assertNotIn(35, fields)
        self.assertNotIn(39, fields)

    def test_all_fragment_boundaries(self):
        raw = packet(2, {231: 45}) + packet(values={115: -5})
        for boundary in range(len(raw) + 1):
            decoder = protocol.FrameDecoder()
            result = decoder.feed(raw[:boundary]) + decoder.feed(raw[boundary:])
            self.assertEqual([k for k, _ in result], [2, 1])

    def test_corrupt_then_valid(self):
        broken = bytearray(packet())
        broken[40] ^= 1
        with self.assertRaises(ValueError):
            protocol.decode_frame(broken)
        decoder = protocol.FrameDecoder()
        self.assertEqual(len(decoder.feed(b'noise' + broken + packet())), 1)

    def test_unknown_length_and_bounded_buffer(self):
        decoder = protocol.FrameDecoder()
        self.assertEqual(decoder.feed(b'\xaa\x55' + b'\xff' * 20000), [])
        self.assertLessEqual(len(decoder.buffer), 1)
        self.assertEqual(len(decoder.feed(packet())), 1)


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_read_only_and_settings(self):
        received = []
        done = asyncio.Event()

        async def serve(reader, writer):
            try:
                writer.write(packet(2, {231: 45}) + packet(values={115: 10}))
                await writer.drain()
                received.append(await reader.read())
            finally:
                writer.close()
                await writer.wait_closed()
                done.set()

        async with await asyncio.start_server(serve, '127.0.0.1', 0) as server:
            port = server.sockets[0].getsockname()[1]
            receiver = client.NeoheatClient('127.0.0.1', port)
            result = await receiver.read_snapshot()
            self.assertEqual(result[2][231], 45)
            self.assertEqual(result[1][115], 10)
            await receiver.close()
            await asyncio.wait_for(done.wait(), 2)
            self.assertEqual(received, [b''])
            self.assertEqual(receiver.settings, {})

    async def test_eof_clears_state(self):
        async def serve(reader, writer):
            writer.close()
            await writer.wait_closed()

        async with await asyncio.start_server(serve, '127.0.0.1', 0) as server:
            receiver = client.NeoheatClient('127.0.0.1', server.sockets[0].getsockname()[1])
            with self.assertRaises(ConnectionError):
                await receiver.read_snapshot()
            self.assertIsNone(receiver.writer)


if __name__ == '__main__':
    unittest.main()
