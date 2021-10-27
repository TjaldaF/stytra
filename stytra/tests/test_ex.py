from time import sleep

from lightparam import Param
import stytra

from stytra.stimulation import Protocol, Pause
from stytra.experiments import VisualExperiment
from stytra.stimulation.stimuli import FullFieldVisualStimulus
from stytra.triggering import Trigger
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import stytra as st
from pathlib import Path
from pkgutil import iter_modules
from importlib import import_module
import pytest


# iterate through the modules in the current package
package_dir = Path(st.__file__).parent / "examples"

protocols = []

for (_, module_name, _) in iter_modules([package_dir]):

    if all([excl not in module_name
                for excl in ["custom", "trigger", "serial", "camera"]]):
        
#         # import the module and iterate through its attributes
            try:
                module = import_module(f"stytra.examples.{module_name}")
            except ImportError as e:
                print("Error in: {}\nSee full message here:\n{}".format(module_name,e))
            
            for attribute_name in dir(module):
                if "Protocol" in attribute_name and attribute_name != "Protocol":
                    protocols.append(getattr(module, attribute_name))
            # attribute = getattr(module, attribute_name)
        # except ModuleNotFoundError:
        #    print(f"Can't import {module}")


@pytest.mark.parametrize("protocol", protocols)
def test_simple(protocol):



    print(protocol)

    assert 2==2