# -*- coding: utf-8 -*-
# This code converts behavioral data from fMRI session into BIDS format, and
# store them in each subject's folder.
# This script is intended to be run on ino.

## The output includes 10 columns, onset, duration, trial_type, delayed_reward, delaytime	and choice.
## event_type       ---> event type
## onset            ---> the onset of the event
## duration         ---> the duration of the event
## trial_type       ---> LongDelay_Behavior or ShortDelay_Behavior
## delayed_reward   ---> rewmag of the delayed option
## delaytime        ---> delay time of the delayed option
## choice           ---> decison on current trial, 0--now, 1--delay, nan--no press
## outcome_mag      ---> reward magnitude of the chosen option
## outcome_delay    ---> delay of the chosen option
## subjective_value ---> subjective value of the delayed option

## Workflow
## 1. read subjinfo from local subject_info csv file, to get fMRI id and BIDS id (two new columns);
## 2. check whether data of the current subject has been converted, if yes, then skip;
## 3. if no, connect to dtb and get trial data;
## 4. iterate over every two seesions:(to put two session into one run)
##      a. get nset, duration, trial_type, delayed_reward, delaytime	and choice of each events;
##      b. PLEASE NOTICE, in fMRI data file, the onset of the 2nd session in one run starts from 0 again,
##         this code calculates the time difference between last trial of 1st session and the 1st trial in
##         the 2nd, and then adds the difference on the onset of events in the 2nd session.
##      c. write converted data into tsv and assign name based on BIDS specification, and adds json file with
##         detailed data describtion inside. 
##      d. conversion information (sucess or fail) will be printed
## 5. db connection is self-closed by helpers

## BUGS
## 1. nan data can't be written as 'n/a' into tsv files as suggested by BIDS, it worked on Windows but not on ubuntu. 
##    However, this is a warning not an error in BIDS validator report, so currently, just ignore it.

import sys,glob
import pandas as pd
import json
from datetime import datetime
import math
import numpy as np
sys.path.append('/media/erlichlab/hdd/Erlichlab_repos') # path for helpers
from helpers import DBUtilsClass as db 

# calculate difference between two onsets in two tasks in the same run
def difference(sess_info):
    sess_1st = dbc.query("select trialtime, j_trial_end from fmri.trials where sessid = %s"%sess_info['id'][0]) # timing info in 1st sess
    sess_2nd = dbc.query("select trialtime, j_trial_end from fmri.trials where sessid = %s"%sess_info['id'][1]) # timing info in 2nd sess
    T1 = sess_1st[0][1] # time length from trigger to 1st trial end in 1st sess
    T2 = (sess_2nd[0][0]-sess_1st[0][0]).seconds # time difference betweem 1st sess and 2nd sess
    T3 = sess_2nd[0][1] # time length from trigger to 1st trial end in 2nd sess
    T_diff = T1 + T2 - T3 # time difference between two sessions' reference points
    diff = [0, T_diff]
    return diff

# write current data into tsv and json files
def filewriter(run_number,data,bidsid):
    tsvfile = '/media/erlichlab/hdd/fMRI_Data_Storage/PostponingVSWaiting/%s/func/%s_task-delay_run-0%s_events.tsv'%(bidsid,bidsid,run_number) 
    jsonfile = '/media/erlichlab/hdd/fMRI_Data_Storage/PostponingVSWaiting/%s/func/%s_task-delay_run-0%s_events.json'%(bidsid,bidsid,run_number) 
    data.to_csv(tsvfile, sep='\t',index=False)
    json_dict = {'onset':{"LongName":"Onset Time",
                          "Units":"seconds"},
                 'duration':{"LongName":"Duration",
                            "Units":"seconds"},
                'event_type':{"LongName":"Event Type",
                              "Description":"Decision, Confirmation, Decision_end (from the onset of decision until the end of that trial) or Confirmation_end (from the onset of confirmation until the end of that trial)"},
                 'trial_type':{"LongName":"Trial Type",
                               "Description":"ShortDelay_fMRI (in seconds) or LongDelay_fMRI (in days)"},
                 'delayed_reward':{"Long Name":"Reward Group",
                             "Description":"Binned Reward Values in Delay Options",
                             "levels":{"Rew-High":"High Reward, Reward > 12", "Rew-Med":"Medium Reward, 8 < Reward <= 12", 
                                       "Rew-Low":"Low Reward <= 8" }},
                 'delaytime':{"Long Name":"Delay Group",
                               "Description":"Binned Delay Values in Delay Options",
                               "levels":{"Delay-High":"High Delay, Delay > 20 seconds (Short Delay) or Delay > 91 days (Long Delay)", 
                                         "Delay-Med":"Medium Delay, 7 seconds < Delay <= 20 seconds (Short Delay) or 29 days < Delay <= 91 days (Long Delay)", 
                                         "Delay-Low":"Low Delay, Delay <= 2 seconds (Short Delay) or Delay <= 29 days (Long Delay)"}},
                 'choice':{"Long Name": "Choice in the Current Trial",
                           "levels":{"0": "Now Reward","1": "Delayed Reward","none":"Subject Missed Choosing"}},
                 'outcome_mag':{"Long Name": "Reward Magnitude of the Chosen Option",
                                "Description": "Numerical value of reward magnitude of the chosen option"},
                 'outcome_delay':{"Long Name": "Delay of the Chosen Option",
                                  "Description": "Numerical value of Delay of the chosen option"},
                 'subjective_value':{"Long Name": "Subjective Value of the Delayed Option",
                                     "Description": "Subjective value = V/(1+KT), where V is the delayed reward magnitude on the current trial, K is the discouting factor and T is the delay time (in days)."}}
    with open(jsonfile,'w',encoding='utf-8') as f:
        json.dump(json_dict,f,indent=4)

# check whether the data files of current subject have been converted
def check_double_conversion(subjid,bidsid):
    file_check = glob.glob('/media/erlichlab/hdd/fMRI_Data_Storage/PostponingVSWaiting/%s/func/%s_task-delay*.tsv'%(bidsid,bidsid)) 
    if len(file_check) == 4:
        return False
    elif len(file_check) == 0:
        return True
    else:
        print('files are missing in subject %s with bidsid as %s.\n'%(subjid,bidsid))

# compute subjective value for each option
def SV(k,delay,rewmag):
    sv = int(rewmag)/(1+k*int(delay))
    return sv

# organize data for the current subject
def data_organization(subjid):
    try:
        # bidsid = sub_list['BIDS_ID'][sub_list['netid']==subjid].values[0] # get bidsid, change, get this form dtb
        bidsid = dbc.query("select BIDS_ID from fmri.subj_ID where subjid = '%s'" %subjid)[0][0]
        k_list = dbc.query("select K_L, K_S from fmri.stanfits_fmri where subjid = '%s'"%subjid)[0]
        k_l = math.exp(k_list[0]) # K value in long task
        k_s = math.exp(k_list[1]/86400) # K value in short task
        print('Data conversion of sub %s with BIDS id %s starts...'%(subjid,bidsid))
        if check_double_conversion(subjid,bidsid):
            # get sessinfo
            sessinfo = sorted(dbc.query("select sessid,treatment from fmri.sessions where subjid = '%s' AND scanner = 1" %subjid)) # get 
            # k_list = dbc.query()
            run_number = 0
            for s in range(0,len(sessinfo),2): # combine two sessions into one run
                DF_ev = pd.DataFrame(columns=['onset','duration','event_type','trial_type','delayed_reward','delaytime','choice',
                                              'outcome_mag','outcome_delay','subjective_value']) # create a df to store organized data
                sess_two = {'id':[sessinfo[s][0], sessinfo[s+1][0]],'treatment':[sessinfo[s][1], sessinfo[s+1][1]]} # two sess info in one run       
                # time difference between onset in the 1st task and the onset of the 2nd task. 
                # It's a list including 0 (added on the 1st task) and a calculated value (added on the 2nd task)
                diff = difference(sess_two)  
                run_number += 1 # The current run number, starts from 1
                for sn in range(len(sess_two['id'])):
                    # create a df to store trial data from database, and yellowRew is used to bin data 
                    DF_trial = pd.DataFrame(columns=['onset_fix','onset_decision','duration_decision',
                                                     'onset_confirmation','duration_confirmation','yellowRew','delay','choice','choice_rand']) 
                    sess = sess_two['id'][sn]
                    data = dbc.query("select trialdata from fmri.trials where sessid = '%s'" %sess)
                    treatment = sess_two['treatment'][sn] # current task type
                    for l in data:  # store trial data in one session
                        dict_trial = json.loads(l[0]) # json data for current trial
                        trial_end = dbc.query("select j_trial_end from fmri.trials where sessid = '%s'" %sess) # trial end time to calculate duration of events of decisionMag and confirmationMag
                        DF_trial = DF_trial.append({'onset_fix':dict_trial['onset_fix'],'onset_decision':dict_trial['onset_decision'],
                                                  'duration_decision':dict_trial['decision_RT'], 'onset_confirmation':dict_trial['onset_confirmation'],
                                                  'duration_confirmation':dict_trial['duration_confirmation_A'],'yellowRew':dict_trial['yellowRew'],
                                                  'delay':dict_trial['delay'],'choice':dict_trial['choice'], 'choice_rand':dict_trial['choice_rand']},ignore_index=True)    
                    for i in range(len(DF_trial)):
                        delayed_reward = DF_trial['yellowRew'][i]
                        delaytime = DF_trial['delay'][i]
                        choice = DF_trial['choice'][i] # 0--now, 1--delay, nan--no press
                        # outcome values assignment
                        if choice == 0:
                            choice = 0
                            outmag = 4
                            outdelay = 0
                        elif choice == 1:
                            choice = 1
                            outmag = DF_trial['yellowRew'][i]
                            outdelay = DF_trial['delay'][i]
                        else:
                            choice_rand = str(DF_trial['choice_rand'][i]) 
                            # if no response on current trial, then choice is nan but the outcome is decided by the choice_rand
                            choice = 'n/a' 
                            if choice_rand == '0.0':
                                outmag = 4
                                outdelay = 0
                            else:
                                outmag = DF_trial['yellowRew'][i]
                                outdelay = DF_trial['delay'][i]
                        # sv = SV_compute(DF_trial) # get subjctive value
                        if treatment == 'ShortDelay_fMRI':
                            sv = SV(k_s,DF_trial['delay'][i],DF_trial['yellowRew'][i])
                        elif treatment == 'LongDelay_fMRI':
                            sv = SV(k_l,DF_trial['delay'][i],DF_trial['yellowRew'][i])
                        else:
                            print("Check task type in sbjective value computation!\n")
                        DF_ev = DF_ev.append({'onset':DF_trial['onset_decision'][i]+diff[sn],'duration':DF_trial['duration_decision'][i],
                                              'event_type':'decision','trial_type':treatment, 'delayed_reward':delayed_reward, 'delaytime':delaytime,'choice':choice,'outcome_mag':outmag,
                                              'outcome_delay':outdelay,'subjective_value':sv}, ignore_index=True)# decision
                        DF_ev = DF_ev.append({'onset':DF_trial['onset_confirmation'][i]+diff[sn],
                                              'duration':DF_trial['duration_confirmation'][i],'event_type':'confirmation','trial_type':treatment, 'delayed_reward':delayed_reward, 'delaytime':delaytime,'choice':choice,'outcome_mag':outmag,'outcome_delay':outdelay,'subjective_value':sv}, ignore_index=True)# confirmation
                        DF_ev = DF_ev.append({'onset':DF_trial['onset_decision'][i]+diff[sn],
                                              'duration':trial_end[i][0]-DF_trial['onset_decision'][i],'event_type':'decision_end','trial_type':treatment, 'delayed_reward':delayed_reward, 'delaytime':delaytime,'choice':choice,'outcome_mag':outmag,'outcome_delay':outdelay,'subjective_value':sv}, ignore_index=True)# decisionMag
                        DF_ev = DF_ev.append({'onset':DF_trial['onset_confirmation'][i]+diff[sn],
                                              'duration':trial_end[i][0]-DF_trial['onset_confirmation'][i],'event_type':'confirmation_end','trial_type':treatment, 'delayed_reward':delayed_reward, 'delaytime':delaytime,'choice':choice,'outcome_mag':outmag,'outcome_delay':outdelay,'subjective_value':sv}, ignore_index=True)# confirmationMag
                filewriter(run_number,DF_ev,bidsid)
                print('subj %s, sess %s and sess %s data has been converted into run %s sucessfully!\n'%(subjid,sess_two['id'][0],sess_two['id'][1],run_number))
        else:
            print('Task event files exist in subject %s with bidsid as %s.\n'%(subjid,bidsid))
    except IndexError:
        print('Current subject %s is not assigned with a bidsid!\n'%subjid)

if __name__ == "__main__":
    dbc = db.Connection() # connect to database
    dbc.use('fmri')
    sub_init = pd.read_csv(r'/media/erlichlab/hdd/Erlichlab_repos/fMRI_delay/Code/Subject_info.csv',header = 0) 
    # sub_temp = sub_init.drop(['zoomed-in L', 'zoomed-in S'], axis=1)
    # sub_list = sub_temp.dropna(axis=0,how='any') # get all subjids whose imaging data have been converted
    # sub_list.reset_index(drop=True, inplace=True)
    # for sub in sub_list['netid']:
    #     data_organization(sub)
