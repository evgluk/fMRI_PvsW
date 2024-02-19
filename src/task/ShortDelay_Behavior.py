# -*- coding: utf-8 -*-
#--------------import stuff----------------------------------------
import os, datetime, copy, random
import newPoints,setup,variables,doodle
from psychopy import event
import functions as fc
import time

#--------------------------Main Code--------------------------------
def ShortDelay_Behavior(var,doo,myPoints,getName=True,getRun=True,sub_id=None,pre_points=0,pre_trials=0,pre_trialsCorrect=0):
    startt = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") # record start time
    var.behavior = True
    var.S = True
    var.group = 'tbd'
    var.bundleList_com = []
    var.rewardGot = pre_trialsCorrect# if it's the second short verbal session in the experiment, rewardGot is accumulated from the first short verbal session
    var.trialCounter = pre_trials# if it's the second short verbal session in the experiment, trialCounter is accumulated from the first short verbal session
    var.points = pre_points # if it's the second short verbal session in the experiment, points are accumulated from the first short verbal session
    var.shortfMRI = True # specify short verbal for specific functions
    fc.setpath() # set up directory
    fN = os.path.basename(__file__) # get expName of this file
    expName, extN = os.path.splitext(fN) # get expName and extN
    stageName = expName[:-14] # get stageName
    expDate = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") # get expDate
    p_num,setiddtb,var,expName = fc.exp_setup_computer(var,doo,getName,getRun,sub_id,expName,expDate) # setup without dtb csv data start recording
    fc.about_to_start_behavior(doo,var)# wait for signal from scanner and get subject ready for task
    var.TotalTrial=50
    fc.stage_instruction(stageName,var,doo) # show subjects stage name (long delay)
    fc.fMRIsetup_computer(var,p_num)
    trialNum = 0
    var.nopress = 0
    var.pll = 0
    while trialNum < var.TotalTrial:
        var = fc.new_trial_setup(var,trialNum)
        fc.fixation_and_ITI(doo,var)
        var,doo,myPoints = fc.draw_init(var,doo,myPoints) # start the first state
        while var.state != 'none': # go through all connected states in one trial
            var,doo,myPoints = fc.funcDic_behavior[var.state](var,doo,myPoints)
        var.trialCounter+=1 # plus 1 in trialCounter
        trialNum +=1
        fc.dataRecord_shortfMRI(var, p_num, expName) # record data for this trial
    #fc.show_bigCoins(var,myPoints) # show the total profits to the subjects
    var.dataFile.close() # close the data file
    var.shortVerbal = False # reset shortVerbal boolean to be False
    endt = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")# record end time
    fc.sessiondataRecord_shortcom(var,p_num,expName,expDate,startt,endt)
    var.S = False
    return p_num,var.point_S, var.trialCounter, var.rewardGot

if __name__ == "__main__":
    #------------make objects----------------------
    # these objects won't be made if the file is called from another file
    myPoints = newPoints.NewPoints()
    var = variables.Variables()
    doo = doodle.Doodle()
    ShortDelay_Behavior(var,doo,myPoints) # run main function
