#!/usr/bin/env python3

import asyncio
import json
from game import SpaceShip
import time

clients = []


class Player:
    def __init__(self, reader, writer):
        self.in_q = asyncio.Queue()
        self.out_q = asyncio.Queue()
        self.reader = reader
        self.writer = writer
        self.ship = SpaceShip((50, 50), (0, 0), (0, 0))


async def send(client):
    while True:
        print("send")
        await asyncio.sleep(0.1)
        msg = client.ship.data()
        if client.writer.is_closing():
            print("connection closed")
            clients.remove(client)
            break
        msg = json.dumps(msg) + "\n"
        client.writer.write(msg.encode())
        await client.writer.drain()


async def recv(client):
    t = time.time()
    while True:
        print("recv")
        await asyncio.sleep(0.01)
        data = await client.reader.readline()
        if len(data) == 0 and client.reader.at_eof():
            print("client disconnected")
            clients.remove(client)
            break
        t = time.time() - t
        if t > 0.1:
            msg = data.decode()
            var = json.loads(msg)
            client.ship.control(var)


async def handle_client(reader, writer):
    client = Player(reader, writer)
    clients.append(client)
    print("client connected")
    await asyncio.gather(send(client), recv(client), game())
    writer.close()


async def game():
    t = time.time()
    while True:
        diff = 0.1  # must fix
        for client in clients:
            client.ship.update(diff)
        t = time.time() - t
        await asyncio.sleep(0.02 - t)


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 55555)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
