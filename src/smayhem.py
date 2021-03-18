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
    def __init__(self, SCREENW, SCREENH, FNAME_BG, reader, writer, init_data):
        screenwh = (SCREENW, SCREENH)
        self.screen = pygame.display.set_mode(screenwh)
        if FNAME_BG is None:
            self.background = Surface((SCREENW, SCREENH))
            self.background.fill((0, 0, 0))
        else:
            self.background = pygame.image.load(FNAME_BG)
            self.background = pygame.transform.scale(self.background, screenwh)
        self.reader = reader
        self.writer = writer
        self.ship = LocalPlayerShip()
        for k, v in init_data.items():
            self.id = k
            self.ship.update(v)
        self.latestupdate = init_data
        self.ships = Group()
        self.ships.add(self.ship)
        self.enemies = {}
        self.control = {"left": 0, "right": 0, "forward": 0}

    def update(self):
        for k, v in self.latestupdate.items():
            if k == self.id:
                self.ship.update(v)
                continue
            enemy = self.enemies.get(k)
            if enemy is None:
                newenemy = LocalEnemyShip(k)
                newenemy.update(v)
                self.enemies[newenemy.id] = newenemy
                self.ships.add(newenemy)
                continue
            else:
                enemy.update(v)

        key = pygame.key.get_pressed()
        self.control["left"] = key[pygame.K_LEFT]
        self.control["right"] = key[pygame.K_RIGHT]
        self.control["forward"] = key[pygame.K_UP]

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.ships.draw(self.screen)

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
        pygame.display.update()
        t - time.time()
        await asyncio.sleep(0.1 - t)


async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 55555)
    data = await reader.readline()
    data = json.loads(data.decode())
    client = MayhemGame(config.SCREENW, config.SCREENH, config.FNAME_BG,
                        reader, writer, data)
    await asyncio.gather(client.recv(), game(client))


if __name__ == "__main__":
    asyncio.run(main())
