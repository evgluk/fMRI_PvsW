# -*- coding: utf-8 -*-
#--------------import stuff----------------------------------------
import os, datetime, copy, random
import newPoints,setup,variables,doodle
from psychopy import event
import functions as fc
import time

#--------------------------Main Code--------------------------------
def ShortDelay_fMRI(var,doo,myPoints,getName=True,getRun=True,sub_id=None,sessID=None,pre_points=0,pre_trials=0,pre_trialsCorrect=0,trialnum=0,trigger=True):
    startt = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") # record start time
    var.rewardGot = pre_trialsCorrect# if it's the second short verbal session in the experiment, rewardGot is accumulated from the first short verbal session
    var.trialCounter = pre_trials# if it's the second short verbal session in the experiment, trialCounter is accumulated from the first short verbal session
    var.points = pre_points # if it's the second short verbal session in the experiment, points are accumulated from the first short verbal session
    var.longfMRI = False
    var.shortfMRI = True # specify short verbal for specific functions
    fc.setpath() # set up directory
    fN = os.path.basename(__file__) # get expName of this file
    expName, extN = os.path.splitext(fN) # get expName and extN
    stageName = expName[:-10] # get stageName
    expDate = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") # get expDate
    p_num,setiddtb,var,expName = fc.exp_setup_fMRI(var,doo,getName,getRun,sub_id,sessID,expName,expDate) # setup without dtb csv data start recording
    if trigger:
        fc.about_to_start(doo,var)# wait for signal from scanner and get subject ready for task
    else:
        fc.about_to_start_behavior(doo,var)# if this task is the second one in current block, no trigger is needed
    fc.stage_instruction(stageName,var,doo)
    var.TotalTrial=trialnum
    fc.fMRIsetup(var,p_num)
    trialNum = 0
    while trialNum < var.TotalTrial:
        var = fc.new_trial_setup_fMRI(var,trialNum)
        fc.fixation_and_ITI(doo,var)
        var,doo,myPoints = fc.draw_init(var,doo,myPoints) # start the first state
        while var.state != 'none': # go through all connected states in one trial
            var,doo,myPoints = fc.funcDic[var.state](var,doo,myPoints)
        var.trialCounter+=1 # plus 1 in trialCounter
        trialNum +=1
        fc.dataRecord_shortfMRI(var, p_num, expName) # record data for this trial
    fc.show_bigCoins(var,myPoints) # show the total profits to the subjects
    var.dataFile.close() # close the data file
    var.shortVerbal = False # reset shortVerbal boolean to be False
    endt = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")# record end time
    fc.sessiondataRecord_shortfMRI(var,p_num,expName,expDate,startt,endt)
    fc.end_block(var,doo)
    return p_num,var.point_S, var.trialCounter, var.rewardGot

if __name__ == "__main__":
    #------------make objects----------------------
    # these objects won't be made if the file is called from another file
    myPoints = newPoints.NewPoints()
    var = variables.Variables()
    doo = doodle.Doodle()
    ShortDelay_fMRI(var,doo,myPoints) # run main function
