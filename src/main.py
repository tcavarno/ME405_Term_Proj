import mlx_cam
import machine
import TurretDriver



def cam_test():
    cam = machine.I2C(1)
    print(f"addy {machine.I2C.scan(cam)}")
    mlx = mlx_cam.MLX_Cam(cam)
    while(1):
        img = mlx.get_image()
        mlx.ascii_image(img.buff)

def main():      
    turret = TurretDriver.TurretDriver()
    turret.yaw_to(180)
    turret.run_action()

if __name__ == "__main__":
    main()