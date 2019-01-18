from stytra.hardware.video.cameras.abstract_class import Camera
import cv2
import numpy as np


class OpenCVCamera(Camera):
    """Class for simple control of a camera such as a webcam using opencv.

    """

    def __init__(self, cam_idx=0, **kwargs):
        """

        Parameters
        ----------
        downsampling : int
            downsampling factor for the camera
        """
        super().__init__(**kwargs)

        # Test if API for the camera is available
        self.cam = cv2.VideoCapture(cam_idx)


    def open_camera(self):
        """ """
        pass

    def set(self, param, val):
        """

        Parameters
        ----------
        param :

        val :


        Returns
        -------

        """
        pass
        # # try:
        # if param == "exposure":
        #     self.cam.set(cv2.cv.CV_CAP_PROP_EXPOSURE, val)
        #
        # if param == "framerate":
        #     self.cam.set(cv2.cv.CV_CAP_PROP_FPS, val)
        #     #self.cam.set_framerate(val)
        # # except xiapi.Xi_error:
        # #     return "Invalid camera parameters"

    def read(self):
        """ """
        ret, frame = self.cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        print(gray.shape)
        print(type(gray))

        return np.zeros((100, 100)) # gray

    def release(self):
        """ """
        self.cam.release()