import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import time
from picarx import Picarx
from parallel_parking import parallel_parking
from k_turning import k_turning

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

            if x == 'w':
                px.run(vel)
                time.sleep(dt)
                px.run(0)
            elif x == 's':
                px.run(-vel)
                time.sleep(dt)
                px.run(0)
            elif x == 'a':
                ang -= dang
                px.turn(ang)
            elif x == 'd':
                ang += dang
                px.turn(ang)
            elif x == 'k':
                k_turning(px, 'left')
            elif x == 'l':
                k_turning(px, 'right')
            elif x == 'h':
                parallel_parking(px, 'left')
            elif x == 'j':
                parallel_parking(px, 'right')
            elif x == 'q':
                break
            else:
                continue

    finally:
        px.stop()
        time.sleep(.2)
