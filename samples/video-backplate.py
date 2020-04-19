# Run a camera feed as a backplate
# --------------------------------

# A camera stream projected to plane attached to the camera so that the video
# stream is running behind a geometry in the scene.
# The video is scaled so it fits the render view vertically and is resized 
# when the render view is resized.

# This class has several features
# - automatic detection of stream resolution
# - automatic show/hide of Environments
# - automatic scene clean up when the stream is stopped

# Usage:
# - See at the end of the file

from vrAEBase import vrAEBase
import vrCamera
import vrMaterialEditor
import vrMaterialPtr
import vrNodeUtils
import vrOSGWidget
import vrScenegraph
from vrFieldAccess import vrFieldAccess
from vrVideoGrab import vrVideoGrab

import math
import threading
import os

class CameraBackplate(vrAEBase):

    def __init__(self, cameraSource):
        vrAEBase.__init__(self)

        self.isStreaming = False

        self.distance = 50000.0
        self.streamingSource = str(cameraSource)
        self.streamingSourceWidth = 1280
        self.streamingSourceHeight = 720

        # Stream Setup
        self.streamingPlaneHeight = 1000
        self.streamSetup = False
        # Stream size can only be set when the stream is running and the width and height are known
        # With this variable we can set the stream size once when the stream is actually started
        self.streamSizeSetup = False

        self.environmentWasVisible = False

        self.videoGrab = None
        self.imageData = None

    def recEvent(self, state):
        vrAEBase.recEvent(self, state)

    def __updateReferences(self):
        '''
        Update all references needed for streaming
        '''
        self.streamingTransform = vrScenegraph.findNode('camera_backplate_node')
        self.streamingScreen = vrScenegraph.findNode(
            'camera_backplate_sceen')
        self.streamingBackground = vrScenegraph.findNode(
            'camera_backplate_background')
        self.environments = vrScenegraph.findNode('Environments')

    def __setup(self):
        # Remove old nodes and material
        self.destroy()

        # inject streaming geometry into the scene
        camera = vrScenegraph.findNode('Perspective')
        self.streamingTransform = vrScenegraph.createNode(
            'Transform', 'camera_backplate_node', camera)
        self.streamingTransform.setLocalTranslation(0, 0, -self.distance)

        self.streamingScreen = vrNodeUtils.createPlane(
            self.streamingPlaneHeight, self.streamingPlaneHeight, 1, 1, 0, 0, 0)
        self.streamingScreen.setName('camera_backplate_sceen')

        self.streamingBackground = vrNodeUtils.createPlane(
            self.streamingPlaneHeight, self.streamingPlaneHeight, 1, 1, 0, 0, 0)
        self.streamingBackground.setName('camera_backplate_background')
        self.streamingBackground.setTranslation(0, 0, -self.distance * 0.05)

        self.streamingTransform.addChild(self.streamingScreen)
        self.streamingTransform.addChild(self.streamingBackground)

        self.streamingMaterial = vrMaterialPtr.findMaterial(
            'camera_backplate_material')
        if self.streamingMaterial.isValid():
            vrMaterialEditor.deleteMaterials([self.streamingMaterial])

        self.videoGrab = vrVideoGrab(
            self.streamingScreen, self.streamingSource, self.streamingSourceWidth, self.streamingSourceHeight)
        self.videoGrab.setActive(True)

        vrMaterialPtr.findMaterial('videograb').setName(
            'camera_backplate_material')
        self.streamingMaterial = vrMaterialPtr.findMaterial(
            'camera_backplate_material')
        self.streamingMaterial.fields().setVec3f('diffuseColor', 0.0, 0.0, 0.0)
        self.streamingMaterial.fields().setVec3f('specularColor', 0.0, 0.0, 0.0)
        self.streamingMaterialFields = self.streamingMaterial.fields()

        self.__updateReferences()

    def start(self):
        '''
        Start streaming from the camera source
        '''
        print('Start video stream...', self)

        self.__setup()

        if self.environments.isValid():
            self.environmentWasVisible = self.environments.fields().getBool('')
            self.environments.setActive(False)

        self.streamSizeSetup = False
        vrScenegraph.showNode(self.streamingTransform)
        t = threading.Timer(0.25, self.__updateStreamSize)
        t.start()

        self.addLoop()
        self.isStreaming = True

    def stop(self):
        '''
        Stop streaming
        '''
        if not hasattr(self, "streamingTransform"):
            return

        print('Stop video stream...', self)

        if self.streamingTransform.isValid():
            vrScenegraph.hideNode(self.streamingTransform)

        self.videoGrab.setActive(False)

        if self.environments.isValid():
            self.environments.setActive(self.environmentWasVisible)

        self.imageData = None

        self.subLoop()
        self.isStreaming = False

    def destroy(self):
        '''
        Remove all geometry and materials that were added to the scene
        '''
        print('Destroy streaming control...', self)

        geometry = vrScenegraph.findNode('camera_backplate_node')
        mat = vrMaterialPtr.findMaterial('camera_backplate_material')

        if geometry.isValid():
            geometry.sub()

        if mat.isValid():
            mat.sub(True)

        if self.videoGrab != None:
            del self.videoGrab

    def __updateStreamSize(self):
        # Main vrAEBase loop that rescales the streaming plane in case the size of the renderview changes
        if not self.streamingTransform.isValid():
            return

        if not self.streamSizeSetup:
            print('Scale stream to renderview dimensions...', self)
            if self.__scaleScreenToVideoData():
                self.streamSizeSetup = True
            else:
                print('Scale stream to renderview dimensions... failed', self)
                return

    def __scaleScreenToVideoData(self):
        '''
        Called once after a new setup of streaming geometry. This will scale the streamning screen geometry to dimensions of the screen.

        Return: True if width and height are set, False otherwise
        '''
        frameData = self.__readFrameData()
        width = float(frameData['width'])
        height = float(frameData['height'])

        if width == 0 or height == 0:
            return False

        aspect = width / height
        self.streamingScreen.setScale(aspect, 1.0, 1.0)
        self.streamingBackground.setScale(2 * aspect, 2 * 1.0, 1.0)

        print('Scaled stream to size {0}x{1}'.format(width, height), self)
        return True

    def __readFrameData(self):
        '''
        When videograb is showing a stream (running or not) this will return a dictionary with
        width, height of this frame as a dictionary
        '''
        if self.imageData is None:
            colorComponentData = vrFieldAccess(
                self.streamingMaterial.fields().getFieldContainer('colorComponentData'))
            videoComponent = vrFieldAccess(
                colorComponentData.getFieldContainer('incandescenceComponent'))
            self.imageData = vrFieldAccess(
                videoComponent.getFieldContainer('image'))

        if self.imageData is not None:
            width = self.imageData.getInt32('width')
            height = self.imageData.getInt32('height')
            return {'width': width, 'height': height}
        else:
            return {'width': 0, 'height': 0}

    def loop(self):
        if not self.streamingTransform.isValid():
            return

        cam = vrCamera.getActiveCameraNode()
        roll = cam.fields().getReal32("roll")
        self.streamingTransform.setRotation(0, 0, roll)

        # Scale streaming plane to exact dimension of the renderview (vertical)
        fov = vrOSGWidget.getFov()
        # Calculate vertical height of renderview in distance of the streamning transform
        renderWindowHeight = 2.0 * self.distance * \
            math.tan(math.radians(fov) / 2.0)
        scale = float(renderWindowHeight) / float(self.streamingPlaneHeight)

        self.streamingTransform.setScale(scale, scale, 1)


# Create CameraBackplate Object, set it active and call start() on it 
# CameraBackplate takes a name of a camera source.
camera_backplate = CameraBackplate("Integrated Webcam")
camera_backplate.setActive(True)
camera_backplate.start()
