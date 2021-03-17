#!/usr/bin/env python3

import pygame
import config
import json
import asyncio
from game import MayhemGame


class Client:
    def __init__(self, reader, writer):
        self.latestupdate = {"pos": (0, 0), "dir": (1, 0), "velocity": (0, 0)}
        self.data = {"left": 0, "right": 0, "forward": 0}
        self.reader = reader
        self.writer = writer


async def send(client):
    while True:
        await asyncio.sleep(0.02)
        msg = client.data
        if msg is None:
            continue
        if client.writer.is_closing():
            print("connection closed")
            break
        msg = json.dumps(msg) + "\n"
        client.writer.write(msg.encode())
        await client.writer.drain()


async def recv(client):
    print(1)
    while True:
        await asyncio.sleep(0.02)
        data = await client.reader.readline()
        if len(data) == 0 and client.reader.at_eof():
            print("client disconnected")
            break
        msg = data.decode()
        client.latestupdate = json.loads(msg)


async def game(client):
    pygame.init()
    pygame.display.set_caption("Space Mayhem")
    game = MayhemGame(config.SCREENW, config.SCREENH, config.FNAME_BG)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(event)
                exit()
        await asyncio.sleep(0.02)
        game.draw()
        data = game.update(client.latestupdate)
        print(data)
        client.data = data
        pygame.display.update()


async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 55555)
    client = Client(reader, writer)
    await asyncio.gather(send(client), recv(client), game(client))


if __name__ == "__main__":
    asyncio.run(main())
