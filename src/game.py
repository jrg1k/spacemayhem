import pygame
import config
import time
import random
from pygame import Vector2
from pygame.sprite import Sprite

"""
Game objects
authors:
Jørgen Kristensen
Ivan Moen
"""


class GameObject:
    """ General game object """

    def __init__(self, pos=(float, float)):
        self.pos = Vector2(pos)


class GameMovingObject(GameObject):
    """ A game object with a velocity vector """

    def __init__(self, pos, velocity=(float, float)):
        super().__init__(pos)
        self.velocity = Vector2(velocity)

    def withingame(self):
        """ Returns boolean value True/False if the object's position is
        within the screen boundaries set within the config file """
        if 0 < self.pos.x < config.SCREENW:
            if 0 < self.pos.y < config.SCREENH:
                return True
        return False


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
        """ Calculates change in position in relation to change over time """

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
        self.respawntime = time.time()
        self.respawned = False

    def update(self, ships, diff=0.0):
        if not self.withingame():
            self.respawn()
            return
        if self.respawned is True:
            if time.time() - self.respawntime > config.PLAYER_RESPAWN:
                self.respawned = False
        self.control(diff)
        self.move(diff)
        for pew in self.projectiles:
            pew.update(ships, diff)

    def control(self, diff):
        """ For handling player controls """
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
                self.projectiles.append(RemoteProjectile(laserpos,
                                                         self.dirvec.xy,
                                                         self.playerid,
                                                         self.projectiles,
                                                         self))
                self.firetime = time.time()
        self.ctrl = 0

    def get_data(self):
        """ Returns a touple containing the objects position, velocity and
        direction, as well as action(player input information), fuel data,
        lives and score """
        data = (self.action,
                (self.pos.x, self.pos.y),
                (self.velocity.x, self.velocity.y),
                (self.dirvec.x, self.dirvec.y),
                self.fuel,
                self.lives,
                self.score,
                self.respawned)
        self.action = 0
        return data

    def respawn(self):
        """ Respawns and looses one health, should trigger if hit by enemy
        laser or flying outside of the map"""
        self.pos = Vector2(100, 100)
        self.dirvec = Vector2(0, -1)
        self.velocity = Vector2(0, 0)
        self.fuel = config.SHIP_FUELTANK
        self.respawned = 1
        self.respawntime = time.time()
        if self.lives == 1:
            self.score -= 1
            self.lives = 5
            return
        self.lives -= 1


class LocalSpaceShip(SpaceShip, Sprite):
    """ Space ship in the context of client:
    drawing sprites, removing sprites and so on """

    def __init__(self, init_data, image, playerid):
        SpaceShip.__init__(self,
                           init_data[1],
                           init_data[2],
                           init_data[3],
                           playerid)
        Sprite.__init__(self)
        self.fuel = init_data[4]
        self.lives = init_data[5]
        self.score = init_data[6]
        self.orig_image = image
        self.set_image()

    def fire(self):
        """ Returns a projectile object """
        projectile_pos = self.pos.xy + self.dirvec.xy * 4
        return LocalProjectile(projectile_pos, self.dirvec.xy, self.playerid)

    def update(self, projectiles, data, diff=0.0):
        """ Takes data from server and updates values locally """
        self.move(diff)
        if data:
            self.pos = Vector2(data[1])
            self.velocity = Vector2(data[2])
            self.dirvec = Vector2(data[3])
            self.fuel = data[4]
            self.lives = data[5]
            self.score = data[6]
            if data[0] & config.ACTION_FIRE:
                projectiles.add(self.fire())
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
        image = pygame.transform.scale(image,
                                       (config.SHIP_SIZE,
                                        config.SHIP_SIZE)).convert_alpha()
        super().__init__(init_data, image, playerid)


class LocalEnemyShip(LocalSpaceShip):
    """ enemy player representation spaceship """

    def __init__(self, init_data, playerid):
        image = pygame.image.load("images/enemy.png")
        image = pygame.transform.scale(image,
                                       (config.SHIP_SIZE,
                                        config.SHIP_SIZE)).convert_alpha()
        super().__init__(init_data, image, playerid)


class Projectile(GameMovingObject):
    """ General projectile class """

    def __init__(self, pos, velocity, playerid=int):
        super().__init__(pos, velocity)
        self.velocity.scale_to_length(config.SHIP_LASER_SPEED)
        self.playerid = playerid

    def move(self, diff=0.0):
        self.pos += (self.velocity * diff)


class RemoteProjectile(Projectile):
    """ Projectile handling server side """

    def __init__(self, pos, velocity, playerid, group, ship):
        super().__init__(pos, velocity, playerid)
        self.group = group
        self.ship = ship

    def update(self, ships, diff=0.0):
        if self.detect_collision(ships):
            return
        self.move(diff)

    def detect_collision(self, ships):
        """ collision detection with ships """
        if not self.withingame():
            self.group.remove(self)
            return True
        hitpoint = self.pos + self.velocity
        for ship in ships:
            if self.playerid == ship.playerid or ship.respawned is True:
                continue
            dist = int(hitpoint.distance_squared_to(ship.pos))
            if dist < config.SHIP_SIZE_SQUARED:
                ship.respawn()
                self.group.remove(self)
                self.ship.score += 1


class LocalProjectile(Sprite, Projectile):
    """ Handling of projectile in the context of local client """

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
        posy = random.randrange(-100, 0)
        velocityx = random.randrange(-100, -50)
        velocityy = random.randrange(0, config.SCREENH)
        planet_type = random.choice(list(config.PLANETS.keys()))
        planet_radius = random.randrange(15, 30)
        planet_speed = random.randrange(2, 6)
        super().__init__((posx, posy),
                         (velocityx, velocityy),
                         planet_type,
                         planet_radius,
                         planet_speed)
        self.velocity.scale_to_length(self.speed)
        self.group = planet_group
        self.objid = self.__hash__()

    def detect_collision(self, ships):
        if self.pos.y > config.SCREENH:
            self.group.remove(self)
            return
        for s in ships:
            dist = int(self.pos.distance_squared_to(s.pos))
            if dist < self.radius_squared:
                s.respawn()

    def update(self, ships):
        self.detect_collision(ships)
        diff = (time.time() - self.updatetime) / config.UPDATE_RATE
        self.move(diff)
        self.updatetime = time.time()

    def get_data(self):
        data = (self.objid,
                (self.pos.x, self.pos.y),
                (self.velocity.x, self.velocity.y),
                self.type,
                self.radius,
                self.speed)
        return data


class LocalPlanet(Sprite, Planet):
    """ Handling of obstacle object in the context of local client """

    def __init__(self, planet_data):
        Sprite.__init__(self)
        Planet.__init__(self,
                        planet_data[1],
                        planet_data[2],
                        planet_data[3],
                        planet_data[4],
                        planet_data[5])
        self.objid = planet_data[0]
        image = pygame.image.load(config.PLANETS[self.type])
        self.image = pygame.transform.scale(image, (self.radius, self.radius))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self, lookup, data, diff):
        if self.withinboundry() is False:
            lookup.pop(self.objid)
            self.kill()
            return
        self.move(diff)
        if data:
            self.pos = Vector2(data[1])
        self.rect.center = self.pos