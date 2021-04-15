#!/usr/bin/env python3

import asyncio
import json
import time
import config
from game import RemoteSpaceShip
from game import RemotePlanet


class Player:
    """
    Player class in the context of server handling
    """

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.playerid = self.__hash__()
        self.ship = RemoteSpaceShip((100, 100), (0, 0), (0, -1), self.playerid)
        self.connected = True
        self.updatetime = 0.0

    def update(self, ships):
        """ Calculates difference factor and updates player data in
        order to maintain a constant animation rate """
        diff = (time.time() - self.updatetime) / config.UPDATE_RATE
        self.ship.update(ships, diff)
        self.updatetime = time.time()

    def get_data(self):
        return self.playerid, self.ship.get_data()

    async def send(self, msg):
        """
        Sends the given data message in a json format to the player.
        """
        if self.writer.is_closing():
            return
        msg = json.dumps(msg) + "\n"
        self.writer.write(msg.encode())
        await self.writer.drain()

    async def recv(self):
        """
        Recieves data from the player. The data is assumed to be in a json
        format.
        """
        while True:
            data = await self.reader.readline()
            if len(data) == 0 and self.reader.at_eof():
                break
            msg = data.decode()
            self.ship.ctrl = json.loads(msg)


class GameServer:
    """ The game server objects contains data about the game and methods for
     player handling and game logic """
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.players = []
        self.ships = []
        self.planets = []

    def start(self):
        """ The asynchronous server routine is started. """
        try:
            asyncio.run(self.server_routine())
        except KeyboardInterrupt:
            print("server stopped")

    async def server_routine(self):
        """
        The server routine asynchronously handles players and game logic
        """
        game_server = await asyncio.start_server(self.handle_player,
                                                 config.ADDRESS, config.PORT)
        print("Server started. Awaiting players.")
        async with game_server:
            await asyncio.gather(game_server.serve_forever(),
                                 self.game_update())

    async def game_update(self):
        while True:
            t = time.time()
            while len(self.planets) < 10:
                self.planets.append(RemotePlanet(self.planets))
            for p in self.planets:
                p.update(self.ships)
            for p in self.players:
                p.update(self.ships)
            data = self.gamedata()
            for p in self.players:
                await p.send(data)
            t = time.time() - t
            await asyncio.sleep(config.UPDATE_RATE - t)

    async def handle_player(self, reader, writer):
        player = Player(reader, writer)
        init_msg = player.get_data()
        await player.send(init_msg)
        self.players.append(player)
        self.ships.append(player.ship)
        print("player connected")
        try:
            await asyncio.create_task(player.recv())
        except ConnectionResetError:
            print("player disconnected")
        player.connected = False
        player.ship.action = player.ship.action | config.ACTION_DC
        writer.close()

    def gamedata(self):
        game_data = []
        players = []
        planets = []
        for p in self.players:
            players.append(p.get_data())
            if p.connected is False:
                self.ships.remove(p.ship)
                self.players.remove(p)
                continue
        for p in self.planets:
            planets.append(p.get_data())
        game_data.append(players)
        game_data.append(planets)
        return game_data


if __name__ == "__main__":
    server = GameServer(config.ADDRESS, config.PORT)
    server.start()
