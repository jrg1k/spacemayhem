import pygame
import config
import time
import random
from pygame import Vector2
from pygame.sprite import Sprite


class GameObject:
    """ General game object """

    def __init__(self, pos=(float, float)):
        self.pos = Vector2(pos)


class GameMovingObject(GameObject):
    def __init__(self, pos, velocity=(float, float)):
        super().__init__(pos)
        self.velocity = Vector2(velocity)


class SpaceShip(GameMovingObject):
    """ The spaceships flying around in space. """

    def __init__(self, pos, velocity, direction=(float, float), playerid=int):
        super().__init__(pos, velocity)
        self.dirvec = Vector2(direction)
        self.dirvec.normalize_ip()
        self.lives = config.PLAYER_LIVES  # TODO: IMPLEMENT HEALTH STUFF
        self.fuel = config.SHIP_FUELTANK  # TODO: IMPLEMENT FUEL STUFF
        self.score = 0
        self.action = 0
        self.playerid = playerid

    def move(self, diff=0.0):
        length = int(self.velocity.length_squared())
        if length > config.SHIP_SPEED_SQARED:
            self.velocity.scale_to_length(config.SHIP_SPEED)
        self.pos += (self.velocity * diff)


class RemoteSpaceShip(SpaceShip):
    """ Spaceship in the context of the game server """

    def __init__(self, pos, velocity, direction, playerid):
        super().__init__(pos, velocity, direction, playerid)
        self.ctrl = 0
        self.projectiles = []
        self.firetime = time.time()

    def update(self, ships, diff=0.0):
        if not self.withingame():
            self.respawn()
            return
        self.control(diff)
        self.move(diff)
        for pew in self.projectiles:
            pew.update(ships, diff)

    def control(self, diff):
        if self.ctrl & config.PCTRL_LEFT:
            self.dirvec = self.dirvec.rotate(-5 * diff)
        if self.ctrl & config.PCTRL_RIGHT:
            self.dirvec = self.dirvec.rotate(5 * diff)
        if self.ctrl & config.PCTRL_THRUST and self.fuel > 0:
            self.fuel -= 1
            self.velocity += self.dirvec * diff * 0.2
        if time.time() - self.firetime >= config.SHIP_FIRERATE:
            if self.ctrl & config.PCTRL_FIRE:
                self.action = self.action | config.ACTION_FIRE
                laserpos = self.pos + self.dirvec * 4
                self.projectiles.append(
                    RemoteProjectile(laserpos, self.dirvec.xy, self.playerid,
                                     self.projectiles))
                self.firetime = time.time()
        self.ctrl = 0

    def withingame(self):
        if 0 < self.pos.x < config.SCREENW:
            if 0 < self.pos.y < config.SCREENH:
                return True
        return False

    def get_data(self):
        data = (((self.pos.x, self.pos.y), (self.velocity.x, self.velocity.y),
                 (self.dirvec.x, self.dirvec.y)), self.action, self.fuel,
                self.lives, self.score)
        self.action = 0
        return data

    def respawn(self):
        self.pos = Vector2(100, 100)
        self.dirvec = Vector2(0, -1)
        self.velocity = Vector2(0, 0)
        self.fuel = config.SHIP_FUELTANK
        self.lives -= 1

    def refuel(self, barrel):
        self.fuel += barrel.fuel


class LocalSpaceShip(SpaceShip, Sprite):
    """ Local handling of spaceships, drawing etc. """

    def __init__(self, init_data, image, playerid):
        SpaceShip.__init__(self, init_data[1], init_data[2], init_data[3],
                           playerid)
        Sprite.__init__(self)
        self.fuel = init_data[4]
        self.lives = init_data[5]
        self.score = init_data[6]
        self.orig_image = image
        self.set_image()

    def fire(self):
        projectile_pos = self.pos.xy + self.dirvec.xy * 2
        return LocalProjectile(projectile_pos, self.dirvec.xy, self.playerid)

    def update(self, projectiles, data, diff=0.0):
        if data:
            self.pos = Vector2(data[1])
            self.velocity = Vector2(data[2])
            self.dirvec = Vector2(data[3])
            self.fuel = data[4]
            self.lives = data[5]
            self.score = data[6]
            if data[0] & config.ACTION_FIRE:
                projectiles.add(self.fire())
        self.move(diff)
        self.set_image()

    def set_image(self):
        angle = self.dirvec.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def collision(self, projectiles):
        pygame.sprite.spritecollide(self, projectiles, True)


class LocalPlayerShip(LocalSpaceShip):
    """ player spaceship """

    def __init__(self, init_data, playerid):
        image = pygame.image.load("images/player.png")
        image = pygame.transform.scale(image, (
            config.SHIP_SIZE, config.SHIP_SIZE)).convert_alpha()
        super().__init__(init_data, image, playerid)


class LocalEnemyShip(LocalSpaceShip):
    """ enemy player representation spaceship """

    def __init__(self, init_data, playerid):
        image = pygame.image.load("images/enemy.png")
        image = pygame.transform.scale(image, (
            config.SHIP_SIZE, config.SHIP_SIZE)).convert_alpha()
        super().__init__(init_data, image, playerid)


class Projectile(GameMovingObject):
    def __init__(self, pos, velocity, playerid=int):
        super().__init__(pos, velocity)
        self.velocity.scale_to_length(config.SHIP_LASER_SPEED)
        self.playerid = playerid

    def move(self, diff=0.0):
        self.pos += (self.velocity * diff)

    def withingame(self):
        if 0 < self.pos.x < config.SCREENW:
            if 0 < self.pos.y < config.SCREENH:
                return True
        return False


class RemoteProjectile(Projectile):

    def __init__(self, pos, velocity, playerid, group):
        super().__init__(pos, velocity, playerid)
        self.group = group

    def update(self, ships, diff=0.0):
        if self.detect_collision(ships):
            return
        self.move(diff)

    def detect_collision(self, ships):
        if not self.withingame():
            self.group.remove(self)
            return True
        hitpoint = self.pos + self.velocity
        for ship in ships:
            dist = int(hitpoint.distance_squared_to(ship.pos))
            if self.playerid != ship.playerid and dist < config.SHIP_SIZE_SQUARED:
                ship.respawn()
                self.group.remove(self)


class Planet(GameMovingObject):
    def __init__(self, pos, velocity, planet_type, planet_radius,
                 planet_speed):
        super().__init__(pos, velocity)
        self.type = planet_type
        self.radius = planet_radius
        self.radius_squared = self.radius ** 2
        self.speed = planet_speed
        self.speed_squared = self.speed ** 2
        self.updatetime = time.time()

    def move(self, diff=0.0):
        self.pos += (self.velocity * diff)

    def withinboundry(self):
        if self.pos.y > config.SCREENH:
            return False
        return True


class RemotePlanet(Planet):
    def __init__(self, planet_group):
        posx = random.randrange(config.SCREENCENTER[0],
                                config.SCREENW + config.SCREENCENTER[0])
        posy = random.randrange(-config.SCREENH, 0)
        velocityx = random.randrange(0, config.SCREENCENTER[0])
        velocityy = random.randrange(config.SCREENH)
        planet_type = random.choice(list(config.PLANETS.keys()))
        planet_radius = random.randrange(15, 30)
        planet_speed = random.randrange(2, 6)
        super().__init__((posx, posy), (velocityx, velocityy), planet_type,
                         planet_radius, planet_speed)
        self.velocity.scale_to_length(self.speed)
        self.group = planet_group
        self.objid = self.__hash__()

    def detect_collision(self, ships):
        if self.pos.y > config.SCREENH:
            self.group.remove(self)
            return True
        for s in ships:
            dist = int(self.pos.distance_squared_to(s.pos))
            if dist < self.radius_squared:
                s.respawn()
                return True
        return False

    def update(self, ships):
        if self.detect_collision(ships):
            return
        diff = (time.time() - self.updatetime) / config.UPDATE_RATE
        self.move(diff)
        self.updatetime = time.time()

    def get_data(self):
        data = (self.objid, (self.pos.x, self.pos.y),
                (self.velocity.x, self.velocity.y), self.type, self.radius,
                self.speed)
        return data


class LocalPlanet(Sprite, Planet):
    """ Handling of obstacle object in the context of local client """

    def __init__(self, planet_data):
        Sprite.__init__(self)
        Planet.__init__(self, planet_data[1], planet_data[2], planet_data[3],
                        planet_data[4], planet_data[5])
        self.objid = planet_data[0]
        self.orig_image = pygame.image.load(config.PLANETS[self.type])

    def update(self, diff=0.0):
        self.move(diff)
        if self.withinboundry() is False:
            self.kill()

    def set_image(self):
        angle = self.velocity.angle_to(1, 0)
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos


class LocalProjectile(Sprite, Projectile):
    """ It's a projectile """

    def __init__(self, pos, velocity, playerid):
        Sprite.__init__(self)
        Projectile.__init__(self, pos, velocity, playerid)
        self.orig_image = pygame.image.load("images/pewpewpew.png")
        self.set_image()

    def update(self, ships, diff=0.0):
        if self.detect_collision(ships):
            return
        self.move(diff)
        self.set_image()

    def detect_collision(self, ships):
        if not self.withingame():
            self.kill()
            return True
        hits = pygame.sprite.spritecollide(self, ships, False)
        for hit in hits:
            if hit.playerid != self.playerid:
                self.kill()
                return True
        return False

    def set_image(self):
        angle = self.velocity.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos


class FuelBarrel(GameObject):

    def __init__(self, pos):
        super().__init__(pos)


class RemoteBarrel(FuelBarrel):
    def __init__(self, pos):
        super().__init__(pos)


class LocalBarrel(FuelBarrel):
    def __init__(self, pos):
        super().__init__(pos)
        self.image = pygame.image.load("barrel.png").convert_alpha()
        self.rect = self.image.get_rect()

# class LocalPlayerScore(pygame.font.Font):
#     def __init__(self, playerid, score):
#         super().__init__()
#         self.font = config.SCORE_FONT
#         self.pos = config.SCORE_POS
