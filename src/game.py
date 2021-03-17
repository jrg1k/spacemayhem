import pygame
from pygame import Surface
from pygame import Vector2
from pygame.sprite import Sprite
from pygame.sprite import Group


class SpaceShip:
    def __init__(self, pos, direction, velocity):
        self.pos = Vector2(pos)
        self.direction = Vector2(direction)
        if self.direction.length_squared() == 0:
            self.direction = Vector2(1, 0)
        else:
            self.direction.normalize_ip()
        self.velocity = Vector2(velocity)

    def update(self, diff=float):
        length = self.velocity.length_squared()
        if length > 36:
            self.velocity.scale_to_length(6)
        self.pos += self.velocity * diff

    def data(self):
        return ({
            "pos": (self.pos.x, self.pos.y),
            "dir": (self.direction.x, self.direction.y),
            "velocity": (self.velocity.x, self.velocity.y)
        })

    def control(self, ctrl, diff=1):
        if ctrl["left"]:
            self.direction = self.direction.rotate(-5 * diff)
        if ctrl["right"]:
            self.direction = self.direction.rotate(5 * diff)
        if ctrl["forward"]:
            self.velocity += self.direction * diff * 0.2


class LocalSpaceShip(Sprite):
    """ its a spaceship """
    def __init__(self, image=Surface):
        super().__init__()
        self.orig_image = image
        self.update({"pos": (0, 0), "dir": (1, 0), "velocity": (0, 0)})

    def update(self, data):
        self.pos = Vector2(data["pos"])
        print(self.pos)
        self.direction = Vector2(data["dir"])
        self.velocity = Vector2(data["velocity"])
        angle = self.direction.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos


class Player(LocalSpaceShip):
    """ player spaceship """
    def __init__(self):
        image = pygame.image.load("player.png")
        image = pygame.transform.scale(image, (20, 20))
        super().__init__(image)


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
        self.player = Player()
        self.ships = Group()
        self.ships.add(self.player)
        self.control = {"left": 0, "right": 0, "forward": 0}

    def update(self, data):
        self.ships.update(data)
        key = pygame.key.get_pressed()
        self.control["left"] = key[pygame.K_LEFT]
        self.control["right"] = key[pygame.K_RIGHT]
        self.control["forward"] = key[pygame.K_UP]
        print(self.control)
        return self.control

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.ships.draw(self.screen)
