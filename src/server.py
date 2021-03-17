#!/usr/bin/env python3

import asyncio
import json
from game import SpaceShip
import time

clients = []

def gamedata(clients):
    msg = {}
    for c in clients:
        msg[c.id] = {
                "pos": (c.ship.pos.x, c.ship.pos.y), 
                "dir": (c.ship.direction.x, c.ship.direction.y), 
                "velocity": (c.ship.velocity.x, c.ship.velocity.y)}
    return msg


class Player:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.ship = SpaceShip((50, 50), (0, 0), (0, 0))
        self.id = self.__hash__()

    def data(self):
        data = {}
        data[self.id] = { 
            "pos": (self.ship.pos.x, self.ship.pos.y),
            "dir": (self.ship.direction.x, self.ship.direction.y),
            "velocity": (self.ship.velocity.x, self.ship.velocity.y)}
        return data

async def send(client, msg):
    if client.writer.is_closing():
        print("connection closed")
        clients.remove(client)
        return
    msg = json.dumps(msg) + "\n"
    client.writer.write(msg.encode())
    await client.writer.drain()


async def recv(client):
    while True:
        data = await client.reader.readline()
        print(data)
        if len(data) == 0 and client.reader.at_eof():
            print("client disconnected")
            clients.remove(client)
            break
        msg = data.decode()
        client.ship.ctrl = json.loads(msg)


async def game():
    while True:
        t = time.time()
        diff = 1.0 # must fix
        for client in clients:
            client.ship.update(diff)
            await send(client, gamedata(clients))
        t = time.time() - t
        await asyncio.sleep(0.02 - t)

async def handle_client(reader, writer):
    client = Player(reader, writer)
    await send(client, client.data())
    clients.append(client)
    print("client connected")
    await asyncio.gather(recv(client), game())
    writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 55555)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
