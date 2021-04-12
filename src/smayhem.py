#!/usr/bin/env python3

import pygame
import config
import json
import time
import asyncio
from game import LocalPlayerShip
from game import LocalEnemyShip
from pygame.sprite import Group
from pygame import Surface


class MayhemGame:
    """ The game """

    def __init__(self, background, reader, writer, init_data,
                 screenwh=(int, int)):
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
        for k, v in init_data.items():
            self.id = k
            self.ship = LocalPlayerShip(self.id, v)
        self.latestupdate = init_data
        self.ships = Group()
        self.ships.add(self.ship)
        self.projectiles = Group()
        self.enemies = {}
        self.control = config.PCTRL_NONE
        self.updatetime = 0.0

    def update(self):
        diff = (time.time() - self.updatetime) / config.UPDATE_RATE
        self.projectiles.update(diff)
        if self.latestupdate is None:
            self.ships.update(None, None, diff)
        else:
            for k, v in self.latestupdate.items():
                if k == self.id:
                    self.ship.update(self.projectiles, v, diff)
                    continue

                if int(k) == v:
                    self.enemies.pop(k)
                    for s in self.ships:
                        if s.id == k:
                            self.ships.remove(s)
                    continue
                enemy = self.enemies.get(k)
                if enemy is None:
                    newenemy = LocalEnemyShip(k, v)
                    self.enemies[newenemy.id] = newenemy
                    self.ships.add(newenemy)
                    continue
                else:
                    enemy.update(self.projectiles, v, diff)
            self.latestupdate = None

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.control = self.control | config.PCTRL_LEFT
        if key[pygame.K_RIGHT]:
            self.control = self.control | config.PCTRL_RIGHT
        if key[pygame.K_UP]:
            self.control = self.control | config.PCTRL_THRUST
        if key[pygame.K_SPACE]:
            self.control = self.control | config.PCTRL_FIRE
        self.updatetime = time.time()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.ships.draw(self.screen)
        self.projectiles.draw(self.screen)

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


async def game(client):
    pygame.init()
    pygame.display.set_caption("Space Mayhem")

    while True:
        t = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(event)
                exit()
        client.draw()
        client.update()
        await client.send()
        client.control = config.PCTRL_NONE
        pygame.display.update()
        t = time.time() - t
        await asyncio.sleep(config.FRAME_UPDATE_RATE - t)


async def main():
    reader, writer = await asyncio.open_connection(config.ADDRESS, config.PORT)
    init_data = await reader.readline()
    init_data = json.loads(init_data.decode())
    client = MayhemGame(config.FNAME_BG, reader, writer, init_data,
                        (config.SCREENW, config.SCREENH))
    try:
        await asyncio.gather(client.recv(), game(client))
    except SystemExit:
        print("game quit")


if __name__ == "__main__":
    asyncio.run(main())

    # assets: https://bigbuckbunny.itch.io/platform-assets-pack
