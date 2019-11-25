from multiprocessing import Process, Queue, Event
from queue import Empty
from time import sleep
import datetime
import numpy as np
from stytra.hardware.motor.stageAPI import Motor
from stytra.hardware.motor.motor_calibrator import MotorCalibrator
from stytra.hardware.video.cameras.spinnaker import SpinnakerCamera
import cv2
from stytra.tracking.pipelines import ImageToDataNode, NodeOutput
from collections import namedtuple
from stytra.collectors.namedtuplequeue import NamedTupleQueue
from scipy.spatial import distance


class SendPositionsProcess(Process):
    def __init__(self):
        super().__init__()
        self.position_queue = NamedTupleQueue()
        self.background = None
        self.old_bg = None

    def run(self):
        cam = SpinnakerCamera()
        cam.open_camera()
        cam.set("exposure", 30)
        start = datetime.datetime.now()
        output_type = namedtuple("dotxy", ["x", "y"])

        while True:
            try:
                im = cam.read()
                if im is not None:
                    start = datetime.datetime.now()
                    cv2.imshow("img", im)
                    cv2.waitKey(1)

                    idxs = np.unravel_index(np.nanargmin(im), im.shape)
                    e = (np.float(idxs[1]), np.float(idxs[0]))

                    point_x = e[0]
                    point_y = e[1]

                    e = (point_x, point_y)

            except (TypeError, IndexError):
                e = (None, None)

            self.position_queue.put(datetime.datetime.now(), output_type(*e))


class ReceiverProcess(Process):
    def __init__(self, dot_position_queue, calib_event, home_event, finished_event, motor_position_queue):
        super().__init__()
        self.position_queue = dot_position_queue
        self.motor_position_queue = motor_position_queue
        self.finished_event = finished_event
        self.calib_event = calib_event
        self.home_event = home_event
        self.jitter_thres = 15
        # self.arena_thres = 60000  # aka 3 cm
        # self.home = 2200000

    def run(self):

        #Initialize the Motor here with standard scale
        self.motor_y = Motor(1, scale=1)
        self.motor_x = Motor(2, scale=1)

        # #Initialize homing sequence:
        self.motor_x.motorminimal()
        self.motor_y.motorminimal()

        ##########
        self.motor_y.open()
        self.motor_x.open()
        output_type = namedtuple("stagexy", ["x_", "y_", "dist_x", "dist_y"])
        last_position = None
        dot_pos = []
        motor_pos = []
        times = []

        #TODO Wait for signal to start from GUI

        while not self.finished_event.is_set():
            #TODO does work by itself but calibrator movement doesnt work after

            # if self.home_event.is_set():
            #     self.motor_x.motorminimal()
            #     self.motor_y.motorminimal()
            #     print ("homing event was called")
            #     self.home_event.clear()

            if self.calib_event.is_set():
                self.motor_x.calibrator_movement()
                self.motor_y.calibrator_movement()
                self.calib_event.clear()
                #todo set x and y

            try:
                tracked_time, last_position = self.position_queue.get(timeout=0.001)
            except Empty:
                pass

            if last_position is not None:
                time = datetime.datetime.now()
                times.append(time)
                pos_x = self.motor_x.get_position()
                pos_y = self.motor_y.get_position()
                motor_pos.append([pos_x, pos_y])
                try:
                    #TODO arena bounds as Params of experiment.

                    # dotx, dotcx = motor_x.move_relative_without_move(distance_x)
                    # doty, dotcy = motor_y.move_relative_without_move(distance_y)
                    # print("dotx,y", dotx, doty, dotcx, dotcy)
                    # print(dotcx ** 2 + dotcy ** 2)
                    # print(self.arena_thres ** 2)
                    distance_x =10
                    distance_y =10
                    # arena bounds check relative to home
                    # if dotcx ** 2 + dotcy ** 2 < self.arena_thres ** 2:
                    #     # TODO does not work - always out of bounds
                    #     print("position inside arena bounds")
                        # jitter filter for camera
                    if distance_x ** 2 + distance_y ** 2 > self.jitter_thres ** 2:
                        print("Moving")
                        #TODO change just get pos and plus distance
                        self.motor_x.move_relative(last_position.f0_x)
                        self.motor_y.move_relative(last_position.f0_y)
                        print(distance_x, distance_y)
                        dot_pos.append([distance_x, distance_y])

                    e = (float(pos_x), float(pos_y), distance_x, distance_y)

                    # else:
                    #     print("motor move command out of arena bounds")

                except (ValueError, TypeError, IndexError):
                    e = (pos_x, pos_y, 0.0, 0.0)

                self.motor_position_queue.put(time, output_type(*e))
                # dd.io.save("stage_movement.h5", pd.DataFrame(dict(time = times,
                #                                                   dots=dot_pos,
                #                                                   motorpos=motor_pos)))
        self.motor_x.close()
        self.motor_y.close()


################################


if __name__ == "__main__":
    event = Event()
    source = SendPositionsProcess()
    receiver = ReceiverProcess(source.position_queue, finished_event=event)
    source.start()
    receiver.start()

    finishUp = True
    sleep(20)
    event.set()
    source.join()
    receiver.join()