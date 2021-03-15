import pygame
from pygame import sprite
from pygame import Surface
from pygame import Vector2
from pygame.sprite import Sprite
from pygame.sprite import Group


class SpaceShip(Sprite):
    """ its a spaceship """

    def __init__(self, image=Surface, pos=(int, int), direction=(int, int),
                 velocity=int):
        super().__init__()
        self.orig_image = image
        self.speed = 0.0
        self.direction = Vector2(direction).normalize()
        self.pos = Vector2(pos)
        self.update(0)

    def update(self, diff=float):
        if self.speed > 6:
            self.speed = 6
        angle = self.direction.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.pos += self.direction * self.speed * diff
        self.rect.center = self.pos
        self.control(diff)

    def control(self, diff):
        print("Must be overridden")


class Player(SpaceShip):
    """ player spaceship """

    def __init__(self, pos, velocity):
        image = pygame.image.load("player.png")
        image = pygame.transform.scale(image, (20, 20))
        super().__init__(image, pos, velocity)

    def control(self, diff):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.direction = self.direction.rotate(-5 * diff)
        if key[pygame.K_RIGHT]:
            self.direction = self.direction.rotate(5 * diff)
        if key[pygame.K_UP]:
            self.speed += 0.2 * diff
        if self.speed > 0.0:
            self.speed -= 0.05 * diff


class MayhemGame:
    """ The game """

    def __init__(self, SCREENW, SCREENH, FNAME_BG):
        screenwh = (SCREENW, SCREENH)
        self.screen = pygame.display.set_mode(screenwh)
        if FNAME_BG is None:
            self.background = Surface((SCREENW, SCREENH))
            self.background.fill((0, 0, 0))
        else:
            self.background = pygame.image.load(FNAME_BG)
            self.background = pygame.transform.scale(self.background, screenwh)
        self.player = Player((50, 50), (1, 0))
        self.ships = Group()
        self.ships.add(self.player)

    def update(self, diff):
        self.ships.update(diff)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.ships.draw(self.screen)
