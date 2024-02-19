# -*- coding: utf-8 -*-
#--------------import stuff----------------------------------------
import LongDelay_fMRI, ShortDelay_fMRI, doodle, setup, variables,newPoints
import os, datetime, json
from psychopy import event
import functions as fc

#-------------make necessary objects------------------------------
myPoints = newPoints.NewPoints()
var = variables.Variables()
doo = doodle.Doodle()

#------------fMRI code, Long-Short--------------------------------
def fMRI_LS(var,doo,myPoints):
    expName = os.path.basename(__file__)[:-7] # get expName of this file
    expDate = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") # get expDate
    var.fMRI = True
    var.point_L = 0 # set total points to 0 for long verbal experiments
    var.point_S = 0 # set total points to 0 for short verbal experiments
    p_num,pick,pay_delay,pay_num,trials_long,points_long = LongDelay_fMRI.LongDelay_fMRI(var,doo,myPoints,trialnum=25) # run the first long verbal session and record the returned info
    var.blockName+=1
    p_num,points_short,trials_short,trialsCorrect_short = ShortDelay_fMRI.ShortDelay_fMRI(var,doo,myPoints,getName=False,getRun=False,sub_id=p_num,trialnum=25,trigger=False) # run short verbal session #1
    
if __name__ == "__main__":
    fMRI_LS(var,doo,myPoints) # call main function
