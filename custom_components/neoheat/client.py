"""TCP stream receiver. Never sends application data to the heat pump."""
import asyncio
from collections import deque
from .protocol import FrameDecoder


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
