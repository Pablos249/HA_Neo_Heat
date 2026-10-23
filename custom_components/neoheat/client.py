"""TCP stream receiver. Never sends application data to the heat pump."""
import asyncio
from collections import deque
from .protocol import FrameDecoder, encode_write


class NeoheatClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.decoder = FrameDecoder()
        self.pending = deque()
        self.settings = {}
        self.telemetry = {}
        self.lock = asyncio.Lock()

    async def close(self):
        writer, self.writer = self.writer, None
        self.reader = None
        self.pending.clear()
        self.decoder = FrameDecoder()
        self.settings = {}
        self.telemetry = {}
        if writer is not None:
            writer.close()
            try:
                async with asyncio.timeout(2):
                    await writer.wait_closed()
            except (OSError, TimeoutError):
                pass

    async def read_snapshot(self):
        """Return next telemetry sample and settings seen on this connection."""
        async with self.lock:
            return await self._read_snapshot()

    async def _read_snapshot(self):
        try:
            async with asyncio.timeout(30):
                if self.reader is None:
                    self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
                while True:
                    if not self.pending:
                        chunk = await self.reader.read(8192)
                        if not chunk:
                            raise ConnectionError("Stream closed")
                        self.pending.extend(self.decoder.feed(chunk))
                    while self.pending:
                        kind, values = self.pending.popleft()
                        if kind == 2:
                            self.settings = values
                        else:
                            self.telemetry = values
                            return {1: dict(self.telemetry), 2: dict(self.settings)}
        except (OSError, TimeoutError, asyncio.CancelledError):
            await self.close()
            raise

    async def write_circuit1_setpoint(self, value: float):
        """Write confirmed parameter 0x25 and wait for settings readback."""
        async with self.lock:
            if self.writer is None or self.decoder.identity is None:
                await self._read_snapshot()
            # Queued frames predate the command and cannot confirm this write.
            self.pending.clear()
            self.writer.write(encode_write(self.decoder.identity, 0x25, value))
            await self.writer.drain()
            try:
                async with asyncio.timeout(15):
                    while True:
                        chunk = await self.reader.read(8192)
                        if not chunk:
                            raise ConnectionError("Stream closed while confirming write")
                        for kind, values in self.decoder.feed(chunk):
                            if kind == 1:
                                self.telemetry = values
                            else:
                                self.settings = values
                                if abs(values.get(163, float("inf")) - value) < 0.01:
                                    return {1: dict(self.telemetry), 2: dict(self.settings)}
            except (OSError, TimeoutError, asyncio.CancelledError):
                await self.close()
                raise
