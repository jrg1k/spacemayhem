#!/usr/bin/env python3

import asyncio
import json
from game import SpaceShip
import time

clients = []


class Player:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.ship = SpaceShip((50, 50), (0, 0), (0, 0))


async def send(client):
    while True:
        t = time.time()
        msg = client.ship.data()
        if client.writer.is_closing():
            print("connection closed")
            clients.remove(client)
            break
        msg = json.dumps(msg) + "\n"
        client.writer.write(msg.encode())
        await client.writer.drain()
        t = time.time() - t
        await asyncio.sleep(0.1 - t)


async def recv(client):
    while True:
        t = time.time()
        data = await client.reader.readline()
        if len(data) == 0 and client.reader.at_eof():
            print("client disconnected")
            clients.remove(client)
            break
        msg = data.decode()
        client.ship.ctrl = json.loads(msg)
        t = time.time() - t
        await asyncio.sleep(0.1 - t)




async def game():
    while True:
        t = time.time()
        diff = 1.0 # must fix
        for client in clients:
            client.ship.update(diff)
        t = time.time() - t
        await asyncio.sleep(0.1 - t)

async def handle_client(reader, writer):
    client = Player(reader, writer)
    clients.append(client)
    print("client connected")
    await asyncio.gather(send(client), recv(client), game())
    writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 55555)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
