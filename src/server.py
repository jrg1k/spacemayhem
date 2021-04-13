#!/usr/bin/env python3

import asyncio
import json
import time
import config
from game import RemoteSpaceShip


class Player:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.ship = RemoteSpaceShip((100, 100), (0, -1), (0, 0))
        self.id = self.__hash__()
        self.connected = True
        self.updatetime = 0.0

    def data(self):
        data = (((self.ship.pos.x, self.ship.pos.y),
                 (self.ship.dirvec.x, self.ship.dirvec.y),
                 (self.ship.velocity.x, self.ship.velocity.y)),
                self.ship.action)
        self.ship.action = config.ACTION_NONE
        return data

    def update(self):
        diff = (time.time() - self.updatetime) / config.UPDATE_RATE
        self.ship.update(diff)
        self.updatetime = time.time()
        #FIX:
        # for p in self.ship.lasers:
        #     if p.withingame() is not True:
        #         self.ship.lasers.remove(p)
        # for p in self.ship.lasers:
        #     print(p.pos.xy)
        ## DOESNT SEEM TO WORK

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
        game_server = await asyncio.start_server(self.handle_player,
                                                 config.ADDRESS, config.PORT)
        addr = game_server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        async with game_server:
            await asyncio.gather(game_server.serve_forever(),
                                 self.game_update())

    async def game_update(self):
        while True:
            t = time.time()
            for p in self.players:
                p.update()
            data = self.gamedata()
            for p in self.players:
                await p.send(data)
            t = time.time() - t
            await asyncio.sleep(config.UPDATE_RATE - t)

    async def handle_player(self, reader, writer):
        player = Player(reader, writer)
        init_msg = {player.id: player.data()}
        await player.send(init_msg)
        self.players.append(player)
        print("player connected")
        try:
            await asyncio.create_task(player.recv())
        except ConnectionResetError:
            print("player disconnected")
        player.connected = False
        writer.close()

    def gamedata(self):
        msg = {}
        for p in self.players:
            if p.connected is False:
                msg[p.id] = p.id
                self.players.remove(p)
                continue
            msg[p.id] = p.data()
        return msg


if __name__ == "__main__":
    server = GameServer(config.ADDRESS, config.PORT)
    server.start()
