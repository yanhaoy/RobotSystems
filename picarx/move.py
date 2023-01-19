from picarx_improved import Picarx
import time


if __name__ == "__main__":
    try:
        px = Picarx()
        px.turn(-30)
        px.run(50)
        time.sleep(1)
        px.run(0)

    finally:
        px.stop()
        time.sleep(.2)
