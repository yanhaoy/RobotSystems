from picarx_improved import Picarx
import time


if __name__ == "__main__":
    try:
        px = Picarx()
        ang = 0

        while 1:
            print('Enter your operation:')
            x = input()

            if x is 'w':
                px.run(50)
                time.sleep(0.5)
                px.run(0)
            elif x is 's':
                px.run(-50)
                time.sleep(0.5)
                px.run(0)
            elif x is 'a':
                ang -= 10
                px.turn(ang)
            elif x is 'd':
                ang += 10
                px.turn(ang)
            elif x is 'q':
                break
            else:
                continue

    finally:
        px.stop()
        time.sleep(.2)
