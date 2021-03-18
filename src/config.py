import sys

if len(sys.argv) < 3:
    print("Usage example: ./run 127.0.0.1 1234")
    exit()

ADDRESS = str(sys.argv[1])
PORT = int(sys.argv[2])
SCREENW = 1600
SCREENH = 900
FNAME_BG = None
