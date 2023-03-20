'''!
    @mainpage ME405
    @section Software_Design
    This project is made up of several files
    Hardware Interface & Controllers: mlx_cam.py, MotorDriver.py, EncoderReader.py, ClosedLoopController.py
    Control Code: task_share.py, cotask.py, TurretDriver.py, turrettest.py
    Tests: camtest.py, camera_viewer.py
    @subsection code The_Code
    @subsubsection mlx_cam mlx_cam.py
    mlx_cam.py is almost entirly unchanged from the provided mlx_cam.py except for the addition
    of a new function 'ascii_image_dfs' that takes a dictionary of points as a way of displaying only
    the blob we are planning on shooting at 

    @subsubsection Taskfiles Taskfiles
    We are using task_share.py and cotask.py in there unedited state.
    
    @subsubsection MotorDriver MotorDriver.py
    This file implments two axis motor driver that is entirly ripped from lab3. This is used to control
    the yaw and pitch axis motors as seen in 'TurretDriver.py'
    
    @subsubsection EncoderReader EncoderReader.py
    This file interfaces with the stm timer modules to count encoder ticks with reasonable over/under flow
    detection. This is used to implement the closed loop control.

    @subsubsection ClosedLoopController ClosedLoopController.py
    This file implements a closed loop p controller used to provide feedback for the pitch and yaw axises
    as seen in 'TurretDriver.py' 

    @subsubsection TurretDriver TurretDriver.py
    This defines and implements the various tasks that are used by the scheduler in order to detect, aim at, and 
    shoot the largest target in a reduced POV in front of the camera. The TurretDriver.py contains methods for adding
    tasks to the scheduler and running the scheduler until forced to stop by a keyboard interrupt.

    @subsubsection camtest camtest.py
    This is the stm code that served as the prototype for the camera tracking code. 
    
    @subsubsection camera_viewer camera_viewer.py
    This file allows a user to receive print statements from the stm and display them in a terminal window such that
    the camera images from mlx_cam can be viewed. This was used for algorithm validation.

    @subsubsection turrettest turrettest.py
    This is the main script to run the turret. It sets up all objects then waits for a button press to start the scheduler

    @subsection Task_Diagram Task_Diagram
    \image html Task_Diagram_Updated.png
    @subsection Pitch_State_Diagram Pitch_State_Diagram 
    \image html Pitch_Diagram.drawio.png
    @subsection Yaw_State_Diagram Yaw_State_Diagram
    \image html "Yaw_Diagram.drawio (copy).png"
    @subsection Shooting_State_Diagram
    \image html Camera.drawio.png
    
'''
