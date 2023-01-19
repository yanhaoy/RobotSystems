from picarx_improved import Picarx
import time


if __name__ == "__main__":
    try:
        px = Picarx()

        # theta_1 = atan((2*wheelbase*abs(par_dis_1))/(forward_dis^2 + par_dis_1^2))
        # theta_2 = atan((4*forward_dis*par_dis_1*wheelbase)/(par_dis_2*(forward_dis^2 + par_dis_1^2)))
        # t_1 = ((pi - 2*atan(forward_dis/par_dis_1))*(forward_dis^2 + par_dis_1^2))/(2*v*abs(par_dis_1))
        # t_2 = (par_dis_2*(forward_dis^2 + par_dis_1^2)*(4*atan(forward_dis/par_dis_1) - 2*pi + 180))/(4*forward_dis*par_dis_1*v)

        px.turn(-30)
        px.run(50)
        time.sleep(0.5)
        px.run(0)

        px.turn(30)
        px.run(-50)
        time.sleep(0.5)
        px.run(0)

        px.turn(-30)
        px.run(50)
        time.sleep(0.5)
        px.run(0)
        
    finally:
        px.stop()
        time.sleep(.2)
