#!/usr/bin/env python3
import asyncio
import json


class Connection:
    def __init__(self, addr=str, port=int):
        self._in = asyncio.Queue()
        self._out = asyncio.Queue()
        asyncio.run(self._connect(addr, port))

    async def _connect(self, addr, port):
        self.reader, self.writer = await asyncio.open_connection(addr, port)
        self._readtask = asyncio.create_task(self._read())
        self._writetask = asyncio.create_task(self._write())

    async def _read(self):
        while True:
            msg = await self.reader.readline()
            if len(msg) == 0 and self.reader.at_eof():
                break
            await self._in.put(json.loads(msg))

    async def _write(self):
        while True:
            msg = await self._out.get()
            self.writer.write(msg.encode)
            await self.writer.drain()

    async def send(self, msg):
        msg = json.dumps(msg) + "\n"
        await self._out.put(msg)
        await self._writetask

    async def get(self):
        await self._readtask
        while True:
            try:
                yield self._in.get_nowait()
            except asyncio.QueueEmpty:
                return

    def exchange(self, msg):
        asyncio.run(self.send(msg))
        asyncio.run(self.get())


conn = Connection("127.0.0.1", 55555)
conn.exchange({"my message": "hey"})
