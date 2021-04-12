from enum import Enum
import sys

if len(sys.argv) < 3:
    print("Usage example: ./run 127.0.0.1 1234")
else:
    ADDRESS = str(sys.argv[1])
    PORT = int(sys.argv[2])

SCREENW = 1600
SCREENH = 900
FNAME_BG = None

# 1 / <updates per second> = <time between each update>
UPDATE_RATE = 1 / 50
FRAME_UPDATE_RATE = 1 / 60

# Player control constants
PCTRL_NONE = 0
PCTRL_LEFT = 1
PCTRL_RIGHT = 2
PCTRL_THRUST = 4
PCTRL_FIRE = 8

# Player actions
ACTION_NONE = 0
ACTION_FIRE = 1
ACTON_DC = 2

