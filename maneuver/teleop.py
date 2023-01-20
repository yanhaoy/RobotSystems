import os
import sys
fpath = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, fpath)
from parallel_parking import parallel_parking
from k_turning import k_turning
import time
from picarx import Picarx


if __name__ == "__main__":
    try:
        px = Picarx()
        vel = 50
        dang = 5
        ang = 0
        dt = 0.25

        while 1:
            print('Enter your operation:')
            x = input()

            if x is 'w':
                px.run(vel)
                time.sleep(dt)
                px.run(0)
            elif x is 's':
                px.run(-vel)
                time.sleep(dt)
                px.run(0)
            elif x is 'a':
                ang -= dang
                px.turn(ang)
            elif x is 'd':
                ang += dang
                px.turn(ang)
            elif x is 'k':
                k_turning(px, 'left')
            elif x is 'l':
                k_turning(px, 'right')
            elif x is 'h':
                parallel_parking(px, 'left')
            elif x is 'j':
                parallel_parking(px, 'right')
            elif x is 'q':
                break
            else:
                continue

    finally:
        px.stop()
        time.sleep(.2)
