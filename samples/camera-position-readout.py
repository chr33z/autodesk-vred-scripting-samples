# Continuously read the camera position and report it via a callback function
# This can also be used to print the camera position to a GUI element

from vrAEBase import vrAEBase
import vrCamera
import vrOSGWidget
import math

# VRED AEBase class that is designed to run in a background loop
class CameraPositionReadout(vrAEBase):
    '''
    Camera Position Readout:
    Read camera position in VRED 3D space and delegate it via the callback

    Returns:
    - height: Height of the camera
    - lookdown: The angle the camera is looking down on the horizontal plane
    - distanceToOrigin: The distance to the origin
    '''

    def __init__(self, callback):
        vrAEBase.__init__(self)
        self.callback = callback
        self.addLoop()

    def recEvent(self, state):
        vrAEBase.recEvent(self, state)

    def loop(self):
        try:
            camera = vrCamera.getActiveCameraNode()
        except:
            camera = vrOSGWidget.getCamNode(0)

        height = camera.getLocalTranslation()[2]
        lookdown = 90 - camera.getRotation()[0]

        x = camera.getLocalTranslation()[0]
        y = camera.getLocalTranslation()[1]
        distance_to_origin = math.sqrt(x ** 2 + y ** 2)

        # Try to pass the camera position to a callback that was passed in the constructor
        try:
            self.callback((height, lookdown, distance_to_origin))
        except:
            pass

# define a callback function that will receive the camera position
def print_camera_position(camera_position):
    print(camera_position)

# Initialize the CameraPositionReadout object 
cameraReadout = CameraPositionReadout(print_camera_position)
# Start the camera position readout by activating it
cameraReadout.setActive(True)