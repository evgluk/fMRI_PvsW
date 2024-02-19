# -*- coding: utf-8 -*-
# Run this file for combined fMRI experiment (longfMRI+shortfMRI+longfMRI+shortfMRI)
#-------------------imports--------------------------------------------------------------------
import LongDelay_Behavior, ShortDelay_Behavior, doodle, setup, variables,newPoints
import os, datetime, json
from psychopy import event
import functions as fc

#---------------Main Function-------------------------------------
def Behavior_combined_even(var,doo,myPoints):
    expName = os.path.basename(__file__)[:-8] # get expName of this file
    expDate = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S") # get expDate
    var.point_L = 0 # set total points to 0 for long verbal experiments
    var.point_S = 0 # set total points to 0 for short verbal experiments
    var.TR = False # stop TR in computer session
    p_num,pick1,pay_delay1,pay_num1,trials_long1,points_long1 = LongDelay_Behavior.LongDelay_Behavior(var,doo,myPoints) # run the first long verbal session and record the returned info
    var.blockName+=1
    fc.block_break(var,doo) # show the break instruction to subject
    p_num,points_short1,trials_short1,trialsCorrect_short1 = ShortDelay_Behavior.ShortDelay_Behavior(var,doo,myPoints,getName=False,getRun=False,sub_id=p_num) # run short verbal session #1
    var.blockName+=1
    fc.block_break(var,doo) # show the break instruction to subject
    p_num,pick2,pay_delay2,pay_num2,trials_long2,points_long2 = LongDelay_Behavior.LongDelay_Behavior(var,doo,myPoints,getName=False,getRun=False,sub_id=p_num,pre_points=points_long1,gettrialn=50,pre_trials=trials_long1) # run the second long verbal session
    var.blockName+=1
    fc.block_break(var,doo) # show the break instruction to subject
    ShortDelay_Behavior.ShortDelay_Behavior(var,doo,myPoints,getName=False,getRun=False,sub_id=p_num,pre_points=points_short1,pre_trials=trials_short1,pre_trialsCorrect=trialsCorrect_short1) # run short verbal session #2
    #print(var.pay,var.pay_num,var.pay_delay)
    session_pay,var.pay = fc.pick_pay(pick1,pick2) # pick one from the two selected trials(in the two long verbal session) to pay the subject
    #print(session_pay,var.pay)
    var.pay_delay,var.pay_num = fc.assign_pay(session_pay,pay_delay1,pay_delay2,pay_num1,pay_num2) # assign the final payment based on the picked trial
    #print(var.pay,var.pay_num,var.pay_delay)
    endt = datetime.datetime.now() # record end time
    fc.payRecord_longfMRI(var,p_num,expName,expDate,endt,session_pay)
    fc.end_instruction(var,doo)
    #fc.end_instruction(doo,trial_pay,session_pay,pay_num,pay_delay,var) # show the ending instruction and picked pay trial to subject

if __name__ == "__main__":
    #-------------make necessary objects------------------------------
    myPoints = newPoints.NewPoints()
    var = variables.Variables()
    doo = doodle.Doodle()
    Behavior_combined_even(var,doo,myPoints) # call main function
