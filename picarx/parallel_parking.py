from picarx_improved import Picarx
import time


if __name__ == "__main__":
    try:
        px = Picarx()

        # t_turn = (wheelbase*acos((2*wheelbase - par_dis*tan(theta))/(2*wheelbase)))/(v*tan(theta))
        # t_forward = (wheelbase*(1 - (2*wheelbase - par_dis*tan(theta))^2/(4*wheelbase^2))^(1/2))/(v*tan(theta))
        
        px.turn(0)
        px.run(50)
        time.sleep(1)
        px.run(0)

        px.turn(30)
        px.run(-50)
        time.sleep(0.5)
        px.run(0)

        px.turn(-30)
        px.run(-50)
        time.sleep(0.5)
        px.run(0)

        px.turn(0)
        px.run(50)
        time.sleep(1)
        px.run(0)
        
    finally:
        px.stop()
        time.sleep(.2)
