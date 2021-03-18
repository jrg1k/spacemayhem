#!/usr/bin/env python3

import asyncio
import json
import time
import config
from game import SpaceShip


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
            return
        msg = json.dumps(msg) + "\n"
        self.writer.write(msg.encode())
        await self.writer.drain()

    async def recv(self):
        while True:
            data = await self.reader.readline()
            if len(data) == 0 and self.reader.at_eof():
                break
            msg = data.decode()
            self.ship.ctrl = json.loads(msg)


class GameServer:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.players = []

    def start(self):
        try:
            asyncio.run(self.server_routine())
        except KeyboardInterrupt:
            print("server stopped")

    async def server_routine(self):
        server = await asyncio.start_server(self.handle_player, config.ADDRESS,
                                            config.PORT)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        async with server:
            await asyncio.gather(server.serve_forever(), self.game_update())

    async def game_update(self):
        while True:
            t = time.time()
            diff = 1.0  # must fix
            for p in self.players:
                p.ship.update(diff)
            data = self.gamedata()
            for p in self.players:
                await p.send(data)
            t = time.time() - t
            await asyncio.sleep(0.02 - t)

    async def handle_player(self, reader, writer):
        player = Player(reader, writer)
        init_msg = {}
        init_msg[player.id] = player.data()
        await player.send(init_msg)
        self.players.append(player)
        print("player connected")
        try:
            await asyncio.create_task(player.recv())
        except ConnectionResetError as e:
            print(e)
        self.players.remove(player)
        print("player disconnected")
        writer.close()

    def gamedata(self):
        msg = {}
        for p in self.players:
            msg[p.id] = p.data()
        return msg


if __name__ == "__main__":
    server = GameServer(config.ADDRESS, config.PORT)
    server.start()
