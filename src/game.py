import pygame
from pygame import Surface
from pygame import Vector2
from pygame.sprite import Sprite


class SpaceShip:
    def __init__(self, pos, direction, velocity):
        self.pos = Vector2(pos)
        self.direction = Vector2(direction)
        if self.direction.length_squared() == 0:
            self.direction = Vector2(1, 0)
        else:
            self.direction.normalize_ip()
        self.velocity = Vector2(velocity)
        self.ctrl = {"left": 0, "right": 0, "forward": 0}

    def update(self, diff=0.0):
        self.control(diff)
        length = int(self.velocity.length_squared())
        if length > 36:
            self.velocity.scale_to_length(6)
        self.pos += (self.velocity * diff)

    def control(self, diff):
        if self.ctrl["left"]:
            self.direction = self.direction.rotate(-5 * diff)
        if self.ctrl["right"]:
            self.direction = self.direction.rotate(5 * diff)
        if self.ctrl["forward"]:
            self.velocity += self.direction * diff * 0.2
        self.ctrl = self.ctrl.fromkeys(self.ctrl, 0)


class LocalSpaceShip(Sprite):
    """ its a spaceship """
    def __init__(self, image=Surface):
        super().__init__()
        self.orig_image = image
        self.update({"pos": (0, 0), "dir": (1, 0), "velocity": (0, 0)})

    def update(self, data):
        self.pos = Vector2(data["pos"])
        self.direction = Vector2(data["dir"])
        self.velocity = Vector2(data["velocity"])
        angle = self.direction.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos


class LocalPlayerShip(LocalSpaceShip):
    """ player spaceship """
    def __init__(self):
        image = pygame.image.load("player.png")
        image = pygame.transform.scale(image, (20, 20))
        super().__init__(image)


class LocalEnemyShip(LocalSpaceShip):
    """ player spaceship """
    def __init__(self, playerid):
        self.id = playerid
        image = pygame.image.load("enemy.png")
        image = pygame.transform.scale(image, (20, 20))
        super().__init__(image)
