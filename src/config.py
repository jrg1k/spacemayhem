import sys

if len(sys.argv) < 3:
    print("Usage example: ./run 127.0.0.1 1234")
    exit()

ADDRESS = str(sys.argv[1])
PORT = int(sys.argv[2])

SCREENW = 1600
SCREENH = 900
FNAME_BG = None

# 1 / <updates per second> = <time between each update>
UPDATE_RATE = 1 / 50
FRAME_UPDATE_RATE = 1 / 60

# Ship parameters
SHIP_FUELTANK = 1000
SHIP_FIRERATE = 1.0
SHIP_SPEED = 6
SHIP_SPEED_SQARED = SHIP_SPEED ** 2
SHIP_SIZE = 20
SHIP_SIZE_SQUARED = SHIP_SIZE ** 2

# Player control constants
PCTRL_LEFT = 1
PCTRL_RIGHT = 2
PCTRL_THRUST = 4
PCTRL_FIRE = 8
FIRE_COOLDOWN = 16
# 01000 AND 10000 for timetrack 1 sec to reduce fire rate?


# Player actions
ACTION_FIRE = 1
ACTON_DC = 2

# Player variables
PLAYER_LIVES = 5
