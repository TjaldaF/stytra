import datetime
import time
from collections import OrderedDict
from multiprocessing import Process, Queue
from datetime import datetime

import numpy as np
import pandas as pd
import inspect

from pyqtgraph.parametertree import Parameter


class Database:
    """ """

    def __init__(self):
        pass

    def inset_experiment_data(self, exp_data):
        """

        Parameters
        ----------
        exp_data : the data collector dictionary
            

        Returns
        -------
        index of database entry

        """
        pass


class FrameProcess(Process):
    """A basic class for a process that deals with frames. It provides
    framerate calculation.

    Parameters
    ----------
        n_fps_frames:
            the maximal number of frames to use to calculate framerate

    Returns
    -------

    """

    def __init__(self, n_fps_frames=10, record_framerate=True):
        super().__init__()

        # Set framerate calculation parameters
        self.n_fps_frames = n_fps_frames
        self.i_fps = 0
        self.previous_time_fps = None
        self.current_framerate = None

        # Store current time timestamp:
        self.current_time = datetime.now()
        self.starting_time = datetime.now()

        self.framerate_queue = Queue()

    def update_framerate(self):
        """Calculate the framerate every n_fps_frames frames."""
        # If number of frames for updating is reached:
        if self.i_fps == self.n_fps_frames - 1:
            self.current_time = datetime.now()
            if self.previous_time_fps is not None:
                try:
                    self.current_framerate = (
                        self.n_fps_frames
                        / (self.current_time - self.previous_time_fps).total_seconds()
                    )
                except ZeroDivisionError:
                    self.current_framerate = 0
                self.framerate_queue.put((self.current_time, (self.current_framerate,)))

            self.previous_time_fps = self.current_time
        # Reset i after every n frames
        self.i_fps = (self.i_fps + 1) % self.n_fps_frames


def prepare_json(it, **kwargs):
    """Used to create a dictionary which will be safe to put in MongoDB

    Parameters
    ----------
    it :
        the item which will be recursively sanitized
    **kwargs :
        paramstree: bool
        convert_datetime: bool
            if datetiems are to be converted to strings for JSON serialization
        eliminate_df: bool
            remove dataframes from the dictionary

    Returns
    -------

    """
    safe_types = (int, float, str)

    for st in safe_types:
        if isinstance(it, st):
            return it
    if isinstance(it, dict):
        new_dict = dict()
        for key, value in it.items():
            new_dict[key] = prepare_json(value, **kwargs)
        return new_dict
    if isinstance(it, tuple):
        tuple_out = tuple([prepare_json(el, **kwargs) for el in it])
        if (
            len(tuple_out) == 2
            and kwargs.get("paramstree", False)
            and isinstance(tuple_out[1], dict)
        ):
            if len(tuple_out[1]) == 0:
                return tuple_out[0]
            else:
                return tuple_out[1]
        else:
            return tuple_out
    if isinstance(it, list):
        return [prepare_json(el, **kwargs) for el in it]
    if isinstance(it, np.generic):
        return np.asscalar(it)
    if isinstance(it, datetime):
        if kwargs.get("convert_datetime", False):
            return it.isoformat()
        else:
            temptime = time.mktime(it.timetuple())
            return datetime.utcfromtimestamp(temptime)
    if isinstance(it, pd.DataFrame):
        if kwargs.get("eliminate_df", False):
            return 0
        else:
            return it.to_dict("list")
    return 0


def get_default_args(func):
    """Find default arguments of functions

    Parameters
    ----------
    func :
        

    Returns
    -------

    """
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def strip_values(it):
    """

    Parameters
    ----------
    it :
        

    Returns
    -------

    """
    if isinstance(it, OrderedDict) or isinstance(it, dict):
        new_dict = dict()
        for key, value in it.items():
            if not key == "value":
                new_dict[key] = strip_values(value)
        return new_dict
    else:
        return it


def get_classes_from_module(input_module, parent_class):
    """Find all the classes in a module that are children of a parent one.

    Parameters
    ----------
    input_module :
        module object
    parent_class :
        parent class object

    Returns
    -------
    type
        OrderedDict of subclasses found

    """
    classes = inspect.getmembers(input_module, inspect.isclass)
    ls_classes = OrderedDict(
        {
            c[1].name: c[1]
            for c in classes
            if issubclass(c[1], parent_class) and not c[1] is parent_class
        }
    )

    return ls_classes
