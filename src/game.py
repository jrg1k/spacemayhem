import pygame
import config
from pygame import Vector2
from pygame.sprite import Sprite


class SpaceShip:
    def __init__(self, posvec, dirvec, velocity):
        self.pos = Vector2(posvec)
        self.dirvec = Vector2(dirvec)
        if self.dirvec.length_squared() == 0:
            self.dirvec = Vector2(0, -1)
        else:
            self.dirvec.normalize_ip()
        self.velocity = Vector2(velocity)

    def move(self, diff=0.0):
        length = int(self.velocity.length_squared())
        if length > 36:  # 6^2 = 36
            self.velocity.scale_to_length(6)
        self.pos += (self.velocity * diff)


class RemoteSpaceShip(SpaceShip):
    def __init__(self, pos, direction, velocity):
        super().__init__(pos, direction, velocity)
        self.ctrl = config.PCTRL_NONE

    def update(self, diff=0.0):
        if not self.withingame():
            self.pos = Vector2(100, 100)
            self.dirvec = Vector2(0, -1)
            self.velocity = Vector2(0, 0)
            return
        self.control(diff)
        self.move(diff)

    def control(self, diff):
        if self.ctrl & config.PCTRL_LEFT:
            self.dirvec = self.dirvec.rotate(-5 * diff)
        if self.ctrl & config.PCTRL_RIGHT:
            self.dirvec = self.dirvec.rotate(5 * diff)
        if self.ctrl & config.PCTRL_THRUST:
            self.velocity += self.dirvec * diff * 0.2
        self.ctrl = config.PCTRL_NONE



class LocalSpaceShip(Sprite, SpaceShip):
    """ its a spaceship """

    def __init__(self, image, pos, dirvec, velocity, playerid):
        Sprite.__init__(self)
        SpaceShip.__init__(self, pos, dirvec, velocity)
        self.orig_image = image
        self.update(((0, 0), (0, -1), (0, 0)))  # pos, dirvec, velocity
        self.id = playerid

    def update(self, data, diff=0.0):
        if data is None:
            self.move(diff)
        else:
            self.pos = Vector2(data[0])
            self.dirvec = Vector2(data[1])
            self.velocity = Vector2(data[2])
        angle = self.dirvec.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos


class LocalPlayerShip(LocalSpaceShip):
    """ player spaceship """

    def __init__(self, playerid, data):
        image = pygame.image.load("player.png")
        image = pygame.transform.scale(image, (20, 20))
        super().__init__(image, data[0], data[1], data[2], playerid)


class LocalEnemyShip(LocalSpaceShip):
    """ player spaceship """

    def __init__(self, playerid, data):
        image = pygame.image.load("enemy.png")
        image = pygame.transform.scale(image, (20, 20))
        super().__init__(image, data[0], data[1], data[2], playerid)


class Projectile:
    def __init__(self, pos, velocity):
        self.pos = pos
        self.velocity = velocity

    def move(self, diff=0.0):
        length = int(self.velocity.length_squared())
        if length > 100:  # 10 = 100
            self.velocity.scale_to_length(10)
        self.pos += (self.velocity * diff)


class RemoteProjectile(Projectile):
    def __init__(self, pos, velocity, playerid):
        super.__init__(pos, velocity)
        self.id = playerid

    def update(self, diff=0.0):
        self.move(diff)



class LocalProjectile(Sprite, Projectile):
    """ It's a projectile"""

    def __init__(self, pos, velocity):
        Projectile.__init__(pos, velocity)
        Sprite.__init__()
        self.orig_image = pygame.image.load("pewpew.png")
        self.update([(0, 0), (0, 0)])  # pos, velocity

    def update(self, data, diff):
        self.move(diff)
        self.pos = Vector2(data[0])
        self.velocity = Vector2(data[1])
        angle = self.velocity.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos


class LandingPlatform:
    def __init__(self, pos):
        self.pos = pos


class RemoteLandingPlatform(LandingPlatform):
    def __init__(self, pos, fueldepot=200):
        super.__init__(pos)
        self.fueldepot = fueldepot


class LocalLandingPlatform(Sprite, LandingPlatform):
    """ A place to land for refuelling """

    def __init__(self, pos):
        Sprite.__init__()
        LandingPlatform.__init__(pos)
        self.image = pygame.image.load("platform.png")
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

# Idea: have fuel barrels you can fly into in order to refuel..?
# class Fuel:
#     def __init__(self):
#         self.fuelamount = 100
