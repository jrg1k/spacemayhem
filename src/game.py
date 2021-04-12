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
        self.health = 100 #TODO: IMPLEMENT HEALTH STUFF
        self.fuel = 100 #TODO: IMPLEMENT FUEL STUFF
        self.action = config.ACTION_NONE

    def move(self, diff=0.0):
        length = int(self.velocity.length_squared())
        if length > 36:  # 6^2 = 36
            self.velocity.scale_to_length(6)
        self.pos += (self.velocity * diff)


class RemoteSpaceShip(SpaceShip):
    def __init__(self, pos, direction, velocity):
        super().__init__(pos, direction, velocity)
        self.ctrl = config.PCTRL_NONE
        self.lasers = []

    def update(self, diff=0.0):
        #TODO: IF LASERS OUT OF SCREEN REMOVE THEM
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
            self.fuel -= 1
            self.velocity += self.dirvec * diff * 0.2
        if self.ctrl & config.PCTRL_FIRE:
            self.action = self.action | config.ACTION_FIRE
            laserpos = self.pos + self.dirvec * 2
            self.lasers.append(RemoteProjectile(laserpos, self.dirvec.xy))

        self.ctrl = config.PCTRL_NONE

    def withingame(self):
        if 0 < self.pos.x < config.SCREENW:
            if 0 < self.pos.y < config.SCREENH:
                return True
        return False


class LocalSpaceShip(Sprite, SpaceShip):
    """ its a spaceship """

    def __init__(self, image, pos, dirvec, velocity, playerid):
        Sprite.__init__(self)
        SpaceShip.__init__(self, pos, dirvec, velocity)
        self.orig_image = image
        self.update(None, None)  # pos, dirvec, velocity
        self.id = playerid

    def fire(self):
        projectile_pos = self.pos.xy + self.dirvec.xy * 2
        return LocalProjectile(projectile_pos, self.dirvec.xy)

    def update(self, projectiles, data, diff=0.0):
        if data is None:
            self.move(diff)
        else:
            self.pos = Vector2(data[0][0])
            self.dirvec = Vector2(data[0][1])
            self.velocity = Vector2(data[0][2])
            if data[1] & config.ACTION_FIRE:
                projectiles.add(self.fire())

        angle = self.dirvec.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos


class LocalPlayerShip(LocalSpaceShip):
    """ player spaceship """

    def __init__(self, playerid, data):
        image = pygame.image.load("player.png")
        image = pygame.transform.scale(image, (20, 20))
        super().__init__(image, data[0][0], data[0][1], data[0][2], playerid)


class LocalEnemyShip(LocalSpaceShip):
    """ player spaceship """

    def __init__(self, playerid, data):
        image = pygame.image.load("enemy.png")
        image = pygame.transform.scale(image, (20, 20))
        super().__init__(image, data[0][0], data[0][1], data[0][2], playerid)


class Projectile:
    def __init__(self, pos, velocity):
        self.pos = Vector2(pos)
        self.velocity = Vector2(velocity)
        self.velocity.scale_to_length(10)

    def move(self, diff=0.0):
        self.pos += (self.velocity * diff)


class RemoteProjectile(Projectile):
    def __init__(self, pos, velocity):
        super().__init__(pos, velocity)

    def update(self, diff=0.0):
        self.move(diff)

    def withingame(self):
        if 0 < self.pos.x < config.SCREENW:
            if 0 < self.pos.y < config.SCREENH:
                return True
        return False


class LocalProjectile(Sprite, Projectile):
    """ It's a projectile """

    def __init__(self, pos, velocity):
        Projectile.__init__(self, pos, velocity)
        Sprite.__init__(self)
        self.orig_image = pygame.image.load("pewpew.png")
        self.update()  # pos, velocity

    def update(self, diff=0.0):
        self.move(diff)
        angle = self.velocity.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos


class LandingPlatform:
    def __init__(self, pos):
        self.pos = pos


class RemoteLandingPlatform(LandingPlatform):
    def __init__(self, pos, fueldepot=200):
        super().__init__(pos)
        self.fueldepot = fueldepot


class LocalLandingPlatform(Sprite, LandingPlatform):
    """ A place to land for refuelling """

    def __init__(self, pos):
        Sprite.__init__(self)
        LandingPlatform.__init__(self, pos)
        self.image = pygame.image.load("platform.png")
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

# Idea: have fuel barrels you can fly into in order to refuel..?
# class Fuel:
#     def __init__(self):
#         self.fuelamount = 100
