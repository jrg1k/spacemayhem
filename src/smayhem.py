#!/usr/bin/env python3
"""
Game client implemententation
authors:
Jørgen Kristensen
Ivan Moen
"""

import pygame
import config
import json
import time
import asyncio
from game import LocalPlayerShip
from game import LocalEnemyShip
from game import LocalPlanet
from pygame.sprite import Group
from pygame import Surface


class MayhemGame:
    """ The game """

    def __init__(self, background, reader, writer, init_data,
                 screenwh=(int, int)):
        # Boilerplate pygame initialization
        pygame.init()
        self.screen = pygame.display.set_mode(screenwh)
        if background is None:
            self.background = Surface(screenwh)
            self.background.fill((0, 0, 0))
        else:
            self.background = pygame.image.load(background)
            self.background = pygame.transform.scale(self.background, screenwh)

        self.reader = reader
        self.writer = writer

        self.playerid = init_data[0]
        self.ship = LocalPlayerShip(init_data[1], self.playerid)
        self.latestupdate = None
        self.ships = Group()
        self.ships.add(self.ship)
        self.projectiles = Group()
        self.planetgroup = Group()
        self.ship_lookup = {}
        self.planet_lookup = {}
        self.control = 0
        self.updatetime = 0.0
        self.font = pygame.font.Font(config.SCORE_FONTNAME,
                                     config.SCORE_FONTSIZE)

        self.infostring = (
            "Lives: {}    Fuel: {}    Score: {}".format(self.ship.lives,
                                                        self.ship.fuel,
                                                        self.ship.score))

    def update(self):
        """ Updating gameinformation """
        diff = (time.time() - self.updatetime) / config.UPDATE_RATE
        self.projectiles.update(self.ships, diff)
        if self.latestupdate is None:
            self.ships.update(None, None, diff)
            self.planetgroup.update(self.planet_lookup, None, diff)
        else:
            self.update_playerships(self.latestupdate[0], diff)
            self.update_planets(self.latestupdate[1], diff)
        self.latestupdate = None
        self.handle_controls()
        self.updatetime = time.time()

    def update_planets(self, planetdata, diff):
        for data in planetdata:
            planet = self.planet_lookup.get(data[0])
            if planet is None:
                newplanet = LocalPlanet(data)
                self.planet_lookup[data[0]] = newplanet
                self.planetgroup.add(newplanet)
                continue
            planet.update(self.planet_lookup, data, diff)

    def update_playerships(self, playerdata, diff):
        # looping through ships
        for data in playerdata:
            if data[0] == self.playerid:
                self.ship.update(self.projectiles, data[1], diff)
                self.infostring = ("Lives: {}    Fuel: {}    Score: {}".format(
                    self.ship.lives,
                    self.ship.fuel,
                    self.ship.score))
                continue

            enemy = self.ship_lookup.get(data[0])
            if enemy is None:
                newenemy = LocalEnemyShip(data[1], data[0])
                self.ship_lookup[newenemy.playerid] = newenemy
                self.ships.add(newenemy)
                continue
            if data[1][0] & config.ACTION_DC:
                enemy.kill()
                self.ship_lookup.pop(data[0])
                continue
            enemy.update(self.projectiles, data[1], diff)

    def handle_controls(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.control = self.control | config.PCTRL_LEFT
        if key[pygame.K_RIGHT]:
            self.control = self.control | config.PCTRL_RIGHT
        if key[pygame.K_UP]:
            self.control = self.control | config.PCTRL_THRUST
        if key[pygame.K_SPACE]:
            self.control = self.control | config.PCTRL_FIRE

    def draw(self):
        """
        Rendering and drawing game information client side
        """
        self.screen.blit(self.background, (0, 0))
        score = self.font.render(self.infostring, True, config.SCORE_FONTCOLOR)
        self.screen.blit(score, config.SCORE_POS)
        self.projectiles.draw(self.screen)
        self.ships.draw(self.screen)
        self.planetgroup.draw(self.screen)

    async def send(self):
        msg = self.control
        if self.writer.is_closing():
            print("connection closed")
            return
        msg = json.dumps(msg) + "\n"
        self.writer.write(msg.encode())
        await self.writer.drain()

    async def recv(self):
        while True:
            data = await self.reader.readline()
            if len(data) == 0 and self.reader.at_eof():
                print("connection closed")
                return
            msg = data.decode()
            self.latestupdate = json.loads(msg)
            print(self.latestupdate[0])


async def game(client):
    pygame.display.set_caption("Space Mayhem")
    while True:
        t = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        client.draw()
        client.update()
        await client.send()
        client.control = 0
        pygame.display.update()
        t = time.time() - t
        await asyncio.sleep(config.FRAME_UPDATE_RATE - t)


async def main():
    try:
        reader, writer = await asyncio.open_connection(config.ADDRESS,
                                                       config.PORT)
    except ConnectionRefusedError:
        print("could not connect to server")
        exit()
    init_data = await reader.readline()
    init_data = json.loads(init_data.decode())
    client = MayhemGame(config.FNAME_BG,
                        reader,
                        writer,
                        init_data,
                        (config.SCREENW, config.SCREENH))
    try:
        await asyncio.gather(client.recv(), game(client))
    except SystemExit:
        print("game quit")


if __name__ == "__main__":
    asyncio.run(main())

"""
Credits: 
Planet sprites: https://helianthus-games.itch.io/animated-pixel-art-planets

"""
