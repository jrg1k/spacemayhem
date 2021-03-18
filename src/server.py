#!/usr/bin/env python3

import asyncio
import json
import time
import config
from game import SpaceShip

players = []


def gamedata():
    msg = {}
    for p in players:
        msg[p.id] = p.data()
    return msg


class Player:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.ship = SpaceShip((50, 50), (0, 0), (0, 0))
        self.id = self.__hash__()

    def data(self):
        data = {
            "pos": (self.ship.pos.x, self.ship.pos.y),
            "dir": (self.ship.direction.x, self.ship.direction.y),
            "velocity": (self.ship.velocity.x, self.ship.velocity.y)
        }
        return data

    async def send(self, msg):
        if self.writer.is_closing():
            print("connection closed")
            players.remove(self)
            return
        msg = json.dumps(msg) + "\n"
        self.writer.write(msg.encode())
        await self.writer.drain()

    async def recv(self):
        while True:
            data = await self.reader.readline()
            if len(data) == 0 and self.reader.at_eof():
                print("connection closed")
                players.remove(self)
                break
            msg = data.decode()
            self.ship.ctrl = json.loads(msg)

    async def update(self):
        while True:
            t = time.time()
            diff = 1.0  # must fix
            self.ship.update(diff)
            await self.send(gamedata())
            t = time.time() - t
            await asyncio.sleep(0.02 - t)


async def init_player(reader, writer):
    player = Player(reader, writer)
    init_msg = {}
    init_msg[player.id] = player.data()
    await player.send(init_msg)
    players.append(player)
    print("player connected")
    try:
        await asyncio.gather(player.recv(), player.update())
    except ConnectionResetError as e:
        print(e)
    writer.close()


async def main():
    server = await asyncio.start_server(init_player, config.ADDRESS,
                                        config.PORT)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
