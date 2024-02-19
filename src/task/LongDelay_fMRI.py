# -*- coding: utf-8 -*-
#--------------import stuff----------------------------------------
import os, datetime, copy, random
import newPoints,setup,variables,doodle
from psychopy import event,core
import functions as fc
import time

#--------------------------Main Code--------------------------------
def LongDelay_fMRI(var,doo,myPoints,getName=True,getRun=True,sub_id=None,sessID=None,pre_points=0,gettrialn=0,pre_trials=0,trialnum=0,trigger=True):
    startt = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") # record start time
    var.trialCounter = pre_trials
    var.rewardGot = gettrialn
    var.point_L = pre_points # if it's the second long verbal session in the experiment, points are accumulated from the first long verbal session
    var.shortfMRI = False
    var.longfMRI = True # specify long verbal for specific functions
    fc.setpath() # set up directory
    fN = os.path.basename(__file__) # get expName of this file
    expName, extN = os.path.splitext(fN) # get expName and extN
    stageName = expName[:-10] # get stageName
    expDate = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")# get expDate
    p_num,setiddtb,var,expName = fc.exp_setup_fMRI(var,doo,getName,getRun,sub_id,sessID,expName,expDate) # setup without dtb csv data start recording
    if trigger:
        fc.about_to_start(doo,var)# wait for signal from scanner and get subject ready for task
    else:
        fc.about_to_start_behavior(doo,var)# if this task is the second one in current block, no trigger is needed
    fc.stage_instruction(stageName,var,doo)
    var.TotalTrial=trialnum
    fc.fMRIsetup(var,p_num)
    var.pay = fc.paymentSelection(var.TotalTrial,var)+gettrialn # select one trial(number) to actually pay the subject
    trialNum = 0
    #set payment variables as None at the start
    var.pay_delay = None
    var.pay_num = None
    while trialNum < var.TotalTrial:
        var = fc.new_trial_setup_fMRI(var,trialNum)
        fc.fixation_and_ITI(doo,var)
        var,doo,myPoints = fc.draw_init(var,doo,myPoints) # start the first state
        while var.state != 'none': # go through all connected states in one trial
            var,doo,myPoints = fc.funcDic[var.state](var,doo,myPoints)
        var.trialCounter+=1 # plus 1 in trialCounter
        trialNum +=1
        if var.trialCounter == var.pay: # assign pay_delay and pay_num if the current trial is the one picked to be actually paid
            if var.presscheck != False:
                if var.choice=='y':
                    var.pay_delay = var.delaymag
                    var.pay_num = var.rewMAG
                else:
                    var.pay_delay = var.shortdelay
                    var.pay_num = var.rewMAG
            else:
                if var.choice_rand == 'y':
                    var.pay_delay = var.delaymag
                    var.pay_num = var.rewMAG
                else:
                    var.pay_delay = var.shortdelay
                    var.pay_num = var.rewMAG
        fc.dataRecord_longfMRI(var, p_num, expName) # record data for this trial
    var.dataFile.close() # close the data file
    var.longfMRI = False # reset longfMRI boolean to be False
    endt = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") # record end time
    fc.sessiondataRecord_longfMRI(var,p_num,expName,expDate,startt,endt)
    fc.end_block(var,doo)
    return p_num, var.pay, var.pay_delay, var.pay_num, var.trialCounter,var.point_L



if __name__ == "__main__":
    #------------make objects----------------------
    # these objects won't be made if the file is called from another file
    myPoints = newPoints.NewPoints()
    var = variables.Variables()
    doo = doodle.Doodle()
    LongDelay_fMRI(var,doo,myPoints) # run main function
