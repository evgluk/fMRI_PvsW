# this file contains some setup information of the experiment
from psychopy import visual, event, gui
import numpy as np  # whole numpy lib is available, prepend 'np.'
import os
import variables

var = variables.Variables()
mywin = visual.Window([1920, 1080], monitor="testMonitor", units="pix",allowGUI=False) # make a windown for all stimuli


# make the Gui to collect subject's info
def dataCollectGui():
    dlg = gui.DlgFromDict(dictionary=var.expInfo, title='LearningStages')
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    else:
        mywin.winHandle.activate()

def username():
    return var.expInfo
