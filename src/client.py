#!/usr/bin/env python3

import asyncio
import time
import json

PORT = 55555

class ConnHandler:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._in_queue = asyncio.Queue()
        self._out_queue = asyncio.Queue()
        asyncio.run(self._connect())

    # Major issue: where do we let the event queue run? Is it enough that send_event is called?
    # Periodic sends will let the receiver run as well. Queueing some async routine in the
    # receiver seems to be enough as well.
    async def _connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        asyncio.create_task(self._reader())
        asyncio.create_task(self._writer())

    async def _reader(self):
        while True:
            msg = await self.reader.readline()
            if len(msg) == 0 and self.reader.at_eof():
                print("Closed stream")
                break
            await self._in_queue.put(json.loads(msg))

    async def _writer(self):
        while True:
            msg = await self._out_queue.get()
            if self.writer.is_closing():
                break
            self.writer.write(msg.encode())
            await self.writer.drain()

    def send_event(self, msg):
        jstr = json.dumps(msg) + "\n"
        asyncio.run(self._out_queue.put(jstr))

    def get_events(self):
        """Yields incoming events until the queue is empty."""
        asyncio.run(self._reader())
        while True:
            try:
                yield self._in_queue.get_nowait()
            except asyncio.QueueEmpty:
                return

conn = ConnHandler("127.0.0.1", 55555)

while True:
    for event in conn.get_events():
        print(event)
