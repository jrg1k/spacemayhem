import sys
"""
Config file for game and server parameters
authors:
Jørgen Kristensen
Ivan Moen
"""


if len(sys.argv) < 3:
    print("Usage example: ./run 127.0.0.1 1234")
    exit()

ADDRESS = str(sys.argv[1])
PORT = int(sys.argv[2])

SCREENW = 1600
SCREENH = 900
SCREENCENTER = (SCREENW / 2, SCREENH / 2)
FNAME_BG = None

# 1 / <updates per second> = <time between each update>
UPDATE_RATE = 1 / 50
FRAME_UPDATE_RATE = 1 / 60

# Ship parameters
SHIP_FUELTANK = 1000
SHIP_FIRERATE = 0.5
SHIP_SPEED = 6
SHIP_SPEED_SQARED = SHIP_SPEED ** 2
SHIP_SIZE = 20
SHIP_SIZE_SQUARED = SHIP_SIZE ** 2
SHIP_LASER_SPEED = 10

# Player control constants
PCTRL_LEFT = 1
PCTRL_RIGHT = 2
PCTRL_THRUST = 4
PCTRL_FIRE = 8

# Score
SCORE_FONTNAME = "freesansbold.ttf"
SCORE_FONTSIZE = 20
SCORE_FONTCOLOR = (255, 255, 255)
SCORE_POS = (10, 10)

# Player actions
ACTION_FIRE = 1
ACTION_DC = 2

# Player variables
PLAYER_LIVES = 5

PLANETS = {
    "barren": "images/Baren.png",
    "ice": "images/Ice.png",
    "lava": "images/Lava.png",
    "terran": "images/Terran.png"}
NUM_PLANETS = 20
