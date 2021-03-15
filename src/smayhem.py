#!/usr/bin/env python3

import pygame
import config
from game import MayhemGame


def main():
    pygame.init()
    pygame.display.set_caption("Space Mayhem")
    game = MayhemGame(config.SCREENW, config.SCREENH, config.FNAME_BG)

    clock = pygame.time.Clock()
    diff = 0.0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(event)
                exit()
        diff = clock.tick(60) / 20
        game.draw()
        game.update(diff)
        pygame.display.update()


if __name__ == "__main__":
    main()
