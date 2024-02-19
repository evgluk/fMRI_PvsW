# -*- coding: utf-8 -*-
# this file contains all the functions needed for all experiments

#-----------------imports---------------------------
  # so that 1/3=0.333 instead of 1/3=0
from psychopy import event,core,gui,visual
import numpy as np  # whole numpy lib is available, prepend 'np.'
import time, datetime, os, random, copy, math
import setup, newPoints, variables,doodle,platform, sys
import csv

# set working path in the computer so that relative packages could work
def setpath():
    if platform.system() == 'Windows': # set path in windows machines
        sys.path.append('/Users/user/repos')
#--------------import helper------------------------
import json

# ask subject for netid from a window shown on the screen
def get_netid(var,doo,dbc,fN):
    expN, extN = os.path.splitext(fN)
    st = datetime.datetime.now()
    expD = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
    p_net = (var.expInfo['Net ID'])
    expGroup = None
    try:
        #p_num, expGroup = sql.r_subjid(dbc,p_net) # get subject id (p_num) and group id given netid
        with open('Subject_info.csv') as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                if str(p_net) in row:
                    p_num = row[0]
                    expGroup = row[1]
                    var.setGroup = row[2]
        print(expGroup)
        if expGroup==3:
            var.Chinese = True
    except expGroup is None: # net_ID is not in the system
        print("net_ID is not in the system!")
        setup.mywin.flip()
        clk = core.CountdownTimer(1.5)
        while clk.getTime() > 0:
            pass
        core.quit()
    #print var.Chinese
    return p_num, var.Chinese, expD, p_net

#Setup for local csv saving in fMRI task.
def exp_setup_computer(var,doo,getName,getRun,sub_id,expName,expDate):
    stt = datetime.datetime.now()
    #-----------------data recording-----------------------------------
    if getName:
        dlg = gui.DlgFromDict(dictionary=var.expInfo_genpop, title=expName)
        if dlg.OK == False:
            core.quit()  # user pressed cancel
        else:
            setup.mywin.winHandle.activate()
        p_net = (var.expInfo_genpop['ID'])
    else:
        p_net = sub_id
    expGroup = None
    with open('Subject_info.csv') as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            if str(p_net) in row:
                p_num = row[0]
                expGroup = row[1]
                var.setGroup = row[2]
                print((var.setGroup))
    if expGroup=='3':
        var.Chinese = True
    elif expGroup == '1':
        var.Chinese = False
    elif expGroup is None: # net_ID is not in the system
        print("net_ID is not in the system!")
        setup.mywin.flip()
        clk = core.CountdownTimer(1.5)
        while clk.getTime() > 0:
            pass
        core.quit()
    # get session number
    if getRun:
        dlg = gui.DlgFromDict(dictionary=var.expRun, title=expName)
        if dlg.OK == False:
            core.quit()  # user pressed cancel
        else:
            setup.mywin.winHandle.activate()
        var.runID = (var.expRun['Run'])
        print((var.runID))
    else:
        var.runID = var.runID
    if var.runID == None: # net_ID is not in the system
        print("run number is not put!")
        setup.mywin.flip()
        clk = core.CountdownTimer(1.5)
        while clk.getTime() > 0:
            pass
        core.quit()
    settingsdtb = json.loads('{"delay": [ 4, 7, 14, 30, 64], "refresherNum": 10, "blockTrial": 2, "passThreshold": 2, "rewdelpair": 10, "ddiscounter": 1.2}')
    setiddtb = 8
    varsetdtb = settingsdtb
    var.delay = varsetdtb['delay']
    var.delaydiscounter = varsetdtb['ddiscounter']
    var.refresherNum = varsetdtb['refresherNum']
    var.blockTrial = varsetdtb['blockTrial']
    var.passThreshold = varsetdtb['passThreshold']
    fileName = 'data/%s_%s_trials_%s.csv' % (p_num, expName, expDate)
    var.dataFile = open(fileName, 'w') # note that MS Excel has only ASCII .csv, other spreadsheets do support UTF-8
    var.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format('expName',
                       'p_num','trialnum','trialtime','stage','rewmag','delay','smag','sdelay','choice','choice_rand','point_L','point_S','j_onset_jittered_fixation','j_duration_jittered_fixation_P','j_duration_jittered_fixation_A',
                       'j_onset_decision','j_decision_RT','j_onset_confirmation','j_duration_confirmation_P','j_duration_confirmation_A','j_onset_clock','j_duration_clock_P','j_duration_clock_A','j_onset_coins','j_duration_coins_P',
                       'j_duration_coins_A','j_compensation_start','j_compensation_end','j_time_compensation','j_press','j_trial_start','j_trial_end','j_trial','j_trial_pay','j_BluePos','j_yellowPos','j_rewMag','j_delay','j_choice',
                       'j_choice_rand','j_yellowRew','j_pay_delay','j_pay_num'))
    var.dataFile.flush()
    return p_num,setiddtb,var,expName

#Setup for local csv saving in fMRI task.
def exp_setup_fMRI(var,doo,getName,getRun,sub_id,runID,expName,expDate):
    stt = datetime.datetime.now()
    #-----------------data recording-----------------------------------
    if getName:
        dlg = gui.DlgFromDict(dictionary=var.expInfo_genpop, title=expName)
        if dlg.OK == False:
            core.quit()  # user pressed cancel
        else:
            setup.mywin.winHandle.activate()
        p_net = (var.expInfo_genpop['ID'])
    else:
        p_net = sub_id
    expGroup = None
    with open('Subject_info.csv') as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            if str(p_net) in row:
                p_num = row[0]
                expGroup = row[1]
                var.setGroup = row[2]
                var.setlabel_L = row[3]
                var.setlabel_S = row[4]
                print((var.setGroup))
    if expGroup=='3':
        var.Chinese = True
    elif expGroup == '1':
        var.Chinese = False
    elif expGroup is None: # net_ID is not in the system
        print("net_ID is not in the system!")
        setup.mywin.flip()
        clk = core.CountdownTimer(1.5)
        while clk.getTime() > 0:
            pass
        core.quit()

    # get session number
    if getRun:
        dlg = gui.DlgFromDict(dictionary=var.expRun, title=expName)
        if dlg.OK == False:
            core.quit()  # user pressed cancel
        else:
            setup.mywin.winHandle.activate()
        var.runID = (var.expRun['Run'])
        print((var.runID))
    else:
        var.runID = var.runID
    if var.runID == None: # net_ID is not in the system
        print("run number is not put!")
        setup.mywin.flip()
        clk = core.CountdownTimer(1.5)
        while clk.getTime() > 0:
            pass
        core.quit()
    settingsdtb = json.loads('{"delay": [ 4, 7, 14, 30, 64], "refresherNum": 10, "blockTrial": 2, "passThreshold": 2, "rewdelpair": 10, "ddiscounter": 1.2}')
    setiddtb = 8
    varsetdtb = settingsdtb
    var.delay = varsetdtb['delay']
    var.delaydiscounter = varsetdtb['ddiscounter']
    var.refresherNum = varsetdtb['refresherNum']
    var.blockTrial = varsetdtb['blockTrial']
    var.passThreshold = varsetdtb['passThreshold']
    fileName = 'data/%s_%s_trials_%s.csv' % (p_num, expName, expDate)
    var.dataFile = open(fileName, 'w') # note that MS Excel has only ASCII .csv, other spreadsheets do support UTF-8
    var.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format('expName',
                       'p_num','trialnum','trialtime','stage','rewmag','delay','smag','sdelay','choice','choice_rand','point_L','point_S','j_onset_jittered_fixation','j_duration_jittered_fixation_P','j_duration_jittered_fixation_A',
                       'j_onset_decision','j_decision_RT','j_onset_confirmation','j_duration_confirmation_P','j_duration_confirmation_A','j_onset_clock','j_duration_clock_P','j_duration_clock_A','j_onset_coins','j_duration_coins_P',
                       'j_duration_coins_A','j_compensation_start','j_compensation_end','j_time_compensation','j_press','j_trial_start','j_trial_end','j_trial','j_trial_pay','j_BluePos','j_yellowPos','j_rewMag','j_delay','j_choice',
                       'j_choice_rand','j_yellowRew','j_pay_delay','j_pay_num'))
    var.dataFile.flush()
    return p_num,setiddtb,var,expName


#fMRI experiment setups--computer session
def fMRIsetup_computer(var,p_num):
    if var.setGroup == '1' or var.setGroup == '4':
        setorder = var.setorder[0] #['A', 'B', 'C', 'D']
        print(setorder)
    elif var.setGroup == '2' or var.setGroup == '3':
        setorder = var.setorder[1] #['C', 'D', 'A', 'B']
        print(setorder)
    else:
        print('wrong choice order setting, please check subj_info.csv')
        sys.exit()
    if var.L:
        setname = 'set_order/' + 'Broad_Long_' + setorder[var.blockName-1] + '.csv'
    elif var.S:
        setname = 'set_order/' + 'Broad_Short_' + setorder[var.blockName-1] + '.csv'
    print(setname)
    with open(setname) as f:
        Choiceset = csv.reader(f)
        for row in Choiceset:
            pair = [int(row[0]),int(row[1])]
            var.bundleList_com.append(pair)
    return var

#fMRI experiment setups--fMRI session
def fMRIsetup(var,p_num):
    if var.setGroup in ['1', '4']:
        setorder = var.setorder[0]
    elif var.setGroup in ['2', '3']: 
        setorder = var.setorder[1]
    else:
        print('wrong choice oder setting, please check subj_info.csv')
        sys.exit()
    if var.runID == '1':
        setorder = setorder[var.blockName - 1]
    elif var.runID == '2':
        setorder = setorder[2 - var.blockName] 
    elif var.runID == '3':
        setorder = setorder[var.blockName + 1]
    elif var.runID == '4':
        setorder = setorder[4 - var.blockName]
    if var.shortfMRI:
        label = 'Short'
    elif var.longfMRI:
        label = 'Long'
    setname = f'set_order/Broad_{label}_{setorder}.csv'
    print(setname)
    var.bundleList_fMRI = []
    bundle_temp = []
    with open(setname) as f:
        Choiceset = csv.reader(f)
        for row in Choiceset:
            pair = [int(row[0]),int(row[1])]
            bundle_temp.append(pair)
    if var.runID == '1' or var.runID == '3':
        var.bundleList_fMRI = bundle_temp[:25]
    elif var.runID == '2' or var.runID == '4':
        var.bundleList_fMRI = bundle_temp[25:]
    return var


# this function selects one trial to actually pay for the participant
def paymentSelection(totalTrialNumber,var):
    num = random.randint(0,totalTrialNumber-1)
    print(num)
    if var.behavior:
        while var.bundleList_com[num][0] > 20:
            num = random.randint(0,totalTrialNumber-1)
    else:
        while var.bundleList_fMRI[num][0] > 20:
            num = random.randint(0,totalTrialNumber-1)
    return num

# show relaxing information
def break_instruction_off(doo,var):
    #doo.instruction.text = u'You may take a short break now.\n\nPress enter if you are ready to start the decision stages.\n\nNote: Keep your headphones on, and if you don\'t hear any sound after pressing enter, please report to the experimenter.'
    if var.Chinese:
        doo.instruction.text = '您现在可以稍作休息.\n\n如果您已准备好开始决策计分阶段，请按“Enter”.\n\n 注意：请带上耳机。如果您在按下“Enter”之后没有听到任何声音, 请立刻告知实验员.'
    else:
        doo.instruction.text = 'You may take a short break now.\n\nPress enter if you are ready to start the decision stages.\n\nNote: Keep your headphones on, and if you don\'t hear any sound after pressing enter, please report to the experimenter.'
    doo.instruction.pos=[0,0]
    doo.instruction.height = 30
    doo.instruction.draw()
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    press = event.waitKeys(keyList="return")
    while press[0]=="return":
        break

#this function transfers cart to polar for the clock
def cart2pol(var,x, y):
    rho = np.sqrt((x-var.clockX)**2 + (y-var.clockY)**2)
    phi = np.arctan2(y-var.clockY, x-var.clockX)
    return(rho, phi)

#this function transfers polar to cart for the clock
def pol2cart(var,rho, phi):
    x = rho * np.cos(phi)+var.clockX
    y = rho * np.sin(phi)+var.clockY
    return(x, y)

#this function gets randomized positions for L and R (jon)
def getRLpos(var):
    if var.Lpos_1 == 3:
        var.Lpos = 2
        var.Rpos = 1
        var.Lpos_1 = 0
    elif var.Lpos_2 == 3:
        var.Lpos = 1
        var.Rpos = 2
        var.Lpos_2 = 0
    else:
        num = random.randint(0,1)
        if num == 0:
            var.Lpos = 1
            var.Rpos = 2
            var.Lpos_1 += 1
        else:
            var.Lpos = 2
            var.Rpos = 1
            var.Lpos_2 += 1

#draws initial choices (jon)
def initText(var,doo):
    doo.choice1.draw()
    doo.choice2.draw()

#this function draws the scales on the clock
def scales(var,doo):
    pi = math.pi
    for i in range(12):
        startX,startY = pol2cart(var,65,i*pi/6)
        endX,endY = pol2cart(var,75,i*pi/6)
        doo.scale.start = (startX,startY)
        doo.scale.end = (endX,endY)
        doo.scale.draw()

def reDrawInitText(var,doo,myPoints):
    if var.Chinese:
        doo.choice1_off.draw()
        doo.choice2_off.draw()
    else:
        initText(var,doo)
    #setup.mywin.flip()

# this function is reminding the subject to focus. Experiment is about to start
def about_to_start(doo, var):
    if var.Chinese:
        doo.chinese_instruction.text = '实验即将开始...'
        doo.chinese_instruction.pos = [0,0]
        doo.chinese_instruction.draw()
    else:
        doo.instruction.text = 'Experiment Starts Soon...'
        doo.instruction.height = 30
        doo.instruction.pos = [0,0]
        doo.instruction.draw()
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    event.waitKeys(keyList=['s'])#fMRI trigger
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    var.starttime = core.getTime()


# this function is reminding the subject to focus. Experiment is about to start
def about_to_start_behavior(doo, var):
    if var.Chinese:
        doo.chinese_instruction.text = '实验即将开始...'
        doo.chinese_instruction.pos = [0,0]
        doo.chinese_instruction.draw()
    else:
        doo.instruction.text = 'Experiment Starts Soon...'
        doo.instruction.height = 30
        doo.instruction.pos = [0,0]
        doo.instruction.draw()
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    clk = core.CountdownTimer(3)
    while clk.getTime() > 0:
        pass
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    var.starttime = core.getTime()

# this function draws fixation and set first ITI in each trial
def fixation_and_ITI(doo,var):
    doo.image.draw()
    blanktime = np.random.normal(4)#set current ITI value
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    var.trial_start = var.onset_jittered_fixation = core.getTime() - var.starttime
    clk = core.CountdownTimer(blanktime+2)
    while clk.getTime() > 0:
        pass
    var.offset_jittered_fixation = core.getTime()-var.starttime
    var.jittered_fixation = blanktime + 2
    return doo,var

#Draws beginning of trial text choices (jon)
def draw_init(var,doo,myPoints):
    getRLpos(var)
    if var.Lpos == 1:
        if var.Chinese:
            doo.choice1_off.pos = [-240,30]
            doo.choice2_off.pos = [240,30]
        else:
            doo.choice1.pos = [-240,30]
            doo.choice2.pos = [240,30]
        var.bluePos = 'L'
        var.yellowPos = 'R'
    else:
        if var.Chinese:
            doo.choice1_off.pos = [240,30]
            doo.choice2_off.pos = [-240,30]
        else:
            doo.choice1.pos = [240,30]
            doo.choice2.pos = [-240,30]
        var.bluePos = 'R'
        var.yellowPos = 'L'
    if var.Chinese:
        if var.longfMRI:
            doo.choice1_off.text = '  今天\n %r 金币' % (var.shortmag)
        else:
            doo.choice1_off.text = '  现在\n %r 金币' % (var.shortmag)
        doo.choice1_off.draw()
        if var.longfMRI:
            doo.choice2_off.text = '%r 天后\n %r 金币' % (var.delaymag,var.rewmag)
        elif var.shortfMRI:
            doo.choice2_off.text = '%r 秒后\n %r 金币' % (var.delaymag,var.rewmag)
        doo.choice2_off.draw()
    else:
        if var.longfMRI:
            doo.choice1.text = '%r coins\ntoday' % (var.shortmag)
        else:
            doo.choice1.text = '%r coins\nnow' % (var.shortmag)
        doo.choice1.text= format_text(doo.choice1.text)
        doo.choice1.draw()
        if var.longfMRI:
            if var.rewmag==1:
                if var.delaymag==1:
                    doo.choice2.text = '%r coin in\n%r day' % (var.rewmag,var.delaymag)
                else:
                    doo.choice2.text = '%r coin in\n%r days' % (var.rewmag,var.delaymag)
            else:
                if var.delaymag==1:
                    doo.choice2.text = '%r coins in\n%r day' % (var.rewmag,var.delaymag)
                else:
                    doo.choice2.text = '%r coins in\n%r days' % (var.rewmag,var.delaymag)
        elif var.shortfMRI:
            if var.rewmag==1:
                doo.choice2.text = '%r coin in\n%r secs' % (var.rewmag,var.delaymag)
            else:
                doo.choice2.text = '%r coins in\n%r secs' % (var.rewmag,var.delaymag)
        doo.choice2.text= format_text(doo.choice2.text)
        doo.choice2.draw()
    setup.mywin.mouseVisible = False
    time_decision_start = setup.mywin.flip()
    var.onset_decision = time_decision_start - var.starttime
    if var.behavior:
        var.state = 'wait_for_choice_behavior'
    else:
        var.state = 'wait_for_choice'
    var.rewMAG = var.rewmag
    return var,doo,myPoints

#this function checks whether user inputs choice (jon)
def wait_for_choice(var,doo,myPoints):
    reDrawInitText(var,doo,myPoints)
    presses = event.waitKeys(maxWait=float(4.0),keyList=['1','2'],timeStamped = True)
    if presses is None:         # Check if response is received in current trial
        var.offset_decision = core.getTime() - var.starttime
        var.decision_RT = var.offset_decision - var.onset_decision
        var.choice_rand = 'none'
        var.presscheck = False
        var.press = var.presscheck
        var.choice = 'none'
        Randnum = random.choice([1,2])
        if Randnum == 1:
            var.choice_rand = 'b'
            var.rewMAG = var.shortmag
        else:
            var.choice_rand = 'y'
            var.rewMAG = var.rewmag
    else:
        var.offset_decision = presses[0][1] - var.starttime
        var.decision_RT = var.offset_decision - var.onset_decision
        var.choice_rand = 'none'
        var.presscheck = True
        var.press = var.presscheck
        var.response = presses[0][0]
    if not var.presscheck:
        pass
    else:
        if presses[0][0] == '1':
            if var.Lpos == 1:
                var.rewMAG = var.shortmag
                var.choice = 'b'
            else:
                var.choice = 'y'
                var.rewMAG = var.rewmag
        elif presses[0][0] == '2':
            if var.Lpos == 2:
                var.rewMAG = var.shortmag
                var.choice = 'b'
            else:
                var.choice = 'y'
                var.rewMAG = var.rewmag
        var.trialsCorrect += 1
    var.state = 'draw_reward'
    return var,doo,myPoints

#this function checks whether user inputs choice (jon)
def wait_for_choice_behavior(var,doo,myPoints):
    reDrawInitText(var,doo,myPoints)
    presses = event.waitKeys(maxWait=float(4.0),keyList=['left','right'],timeStamped = True)
    if presses is None:         # Check if response is received in current trial
        var.offset_decision = core.getTime() - var.starttime
        var.decision_RT = var.offset_decision - var.onset_decision
        var.choice_rand = 'none'
        var.presscheck = False
        var.press = var.presscheck
        var.choice = 'none'
        Randnum = random.choice([1,2])
        if Randnum == 1:
            var.choice_rand = 'b'
            var.rewMAG = var.shortmag
        else:
            var.choice_rand = 'y'
            var.rewMAG = var.rewmag
    else:
        var.offset_decision = presses[0][1] - var.starttime
        var.decision_RT = var.offset_decision - var.onset_decision
        var.choice_rand = 'none'
        var.presscheck = True
        var.press = var.presscheck
        var.response = presses[0][0]
    if not var.presscheck:
        var.nopress += 1
        pass
    else:
        if presses[0][0] == 'left':
            if var.Lpos == 1:
                var.rewMAG = var.shortmag
                var.choice = 'b'
            else:
                var.choice = 'y'
                var.rewMAG = var.rewmag
                if var.blockName < 3:
                    var.pll += 1
        elif presses[0][0] == 'right':
            if var.Lpos == 2:
                var.rewMAG = var.shortmag
                var.choice = 'b'
            else:
                var.choice = 'y'
                var.rewMAG = var.rewmag
                if var.blockName < 3:
                    var.pll += 1
        #timeEnd1 = core.getTime()
        var.trialsCorrect += 1
    var.state = 'draw_reward_behavior'
    return var,doo,myPoints

# Show the reward chosen by the subject in fMRI tasks
def draw_reward(var,doo,myPoints):
    reDrawInitText(var,doo,myPoints)
    if var.presscheck:
        rect = visual.Rect(win=setup.mywin,units="pix",lineWidth=6.0,width=270,height=180,fillColor=None,lineColor='lightgray')
        if var.response == '1':
            rect.pos=[-240,15]
        elif var.response == '2':
            rect.pos=[240,15]
        rect.draw()
    else:
        rect1 = visual.Rect(win=setup.mywin,units="pix",lineWidth=6.0,width=270,height=180,fillColor=None,lineColor='red')
        rect2 = visual.Rect(win=setup.mywin,units="pix",lineWidth=6.0,width=270,height=180,fillColor=None,lineColor='red')
        rect1.pos=[-240,15]
        rect2.pos=[240,15]
        rect1.draw()
        rect2.draw()
        print('no press')
    var.state = 'draw_rewardShort'
    starttime = setup.mywin.flip()
    var.onset_confirmation = starttime - var.starttime
    if var.shortfMRI:
        var.compensation_time1 = core.getTime() - var.starttime
    clk = core.CountdownTimer(0.5)
    while clk.getTime() > 0:
        var.offset_confirmation = core.getTime() - var.starttime
    if var.longfMRI:
        var.point_L += var.rewMAG
        var.state = 'none'
    else:
        #reset all clock- and coin-related variables in short task
        var.new_delayTime = 0
        var.new_delayTime = 0
        var.onset_clock = 0
        var.offset_clock = 0
        var.onset_coins = 0
        var.offset_coins = 0
#    blanktime = random.uniform(0.5, 2.0)#set the second ITI value
#    time_ITI_start = setup.mywin.flip()#show blank screen
#    var.onset_ITI_2nd = time_ITI_start - var.starttime
#    clk = core.CountdownTimer(blanktime)
#    while clk.getTime() > 0:
#        time_ITI_end = core.getTime()
#    var.offset_ITI_2nd = time_ITI_end - var.starttime
    if var.longfMRI:
        var.trial_end = core.getTime() - var.starttime
    else:
        var.compensation_time2 = core.getTime() - var.starttime
        var.time_compensation = var.compensation_time2 - var.compensation_time1
#    var.second_ITI = blanktime
    return var,doo,myPoints

# Show the reward chosen by the subject in behavior tasks
def draw_reward_behavior(var,doo,myPoints):
    reDrawInitText(var,doo,myPoints)
    if var.presscheck:
        rect = visual.Rect(win=setup.mywin,units="pix",lineWidth=6.0,width=270,height=180,fillColor=None,lineColor='lightgray')
        if var.response == 'left':
            rect.pos=[-240,15]
        elif var.response == 'right':
            rect.pos=[240,15]
        rect.draw()
    else:
        rect1 = visual.Rect(win=setup.mywin,units="pix",lineWidth=6.0,width=270,height=180,fillColor=None,lineColor='red')
        rect2 = visual.Rect(win=setup.mywin,units="pix",lineWidth=6.0,width=270,height=180,fillColor=None,lineColor='red')
        rect1.pos=[-240,15]
        rect2.pos=[240,15]
        rect1.draw()
        rect2.draw()
        print('no press')
    var.state = 'draw_rewardShort'
    starttime = setup.mywin.flip()
    var.onset_confirmation = starttime - var.starttime
    if var.shortfMRI:
        var.compensation_time1 = core.getTime() - var.starttime
    clk = core.CountdownTimer(0.5)
    while clk.getTime() > 0:
        var.offset_confirmation = core.getTime()-var.starttime
    if var.longfMRI:
        var.point_L += var.rewMAG
        var.state = 'none'
    else:
        #reset all clock- and coin-related variables in short task
        var.new_delayTime = 0
        var.new_delayTime = 0
        var.onset_clock = 0
        var.offset_clock = 0
        var.onset_coins = 0
        var.time_coins = 0 # reset var.time_coins
        var.offset_coins = 0
#    blanktime = random.uniform(0.5, 2.0)#set the second ITI value
#    time_ITI_start = setup.mywin.flip()#show blank screen
#    var.onset_ITI_2nd = time_ITI_start - var.starttime
#    clk = core.CountdownTimer(blanktime)
#    while clk.getTime() > 0:
#        time_ITI_end = core.getTime()
#    var.offset_ITI_2nd = time_ITI_end - var.starttime
    if var.longfMRI:
        var.trial_end = core.getTime() - var.starttime
    else:
        var.compensation_time2 = core.getTime() - var.starttime
        var.time_compensation = var.compensation_time2 - var.compensation_time1
#    var.second_ITI = blanktime
    return var,doo,myPoints

def delayCircle(var,doo):
    doo.circle.size = 150
    doo.circle.pos = [0,240]
    doo.circle.fillColor=var.purple
    doo.circle.draw()
    doo.circle.size=var.circle_fullSize

#this function generates the empty circle for the clock
def delayCircleEmpty(var,doo):
    doo.circle.size = 150
    doo.circle.pos = [0,240]
    doo.circle.fillColor=var.gray2
    doo.circle.draw()
    doo.circle.size=var.circle_fullSize

#this functions draws the delay countdown clock
def clock(var,doo,myPoints):
    var.delayStart = core.getTime()
    delayEnd = core.getTime()
    var.new_delayTime = var.delaymag-var.time_compensation
    var.onset_clock = core.getTime() - var.starttime
    while delayEnd-var.delayStart<=var.new_delayTime:
        var.secPos2 = 'TBD'
        var.secPos = np.floor(50*(delayEnd-var.delayStart))*(360-var.time_compensation*360/var.delaymag)/(50*var.new_delayTime)
        if var.secPos != var.secPos2:
            myPoints.totalUpdate(var.point_S)
            delayCircle(var,doo)
            scales(var,doo)
            doo.clock.visibleWedge = (0,var.time_compensation*360/var.delaymag + var.secPos)#visible change starts from non-original point
            doo.clock.draw()
            scales(var,doo)
            setup.mywin.flip()
        var.secPos2 = copy.copy(var.secPos)
        delayEnd = core.getTime()
    myPoints.totalUpdate(var.points)
    setup.mywin.flip(clearBuffer=True)
    var.offset_clock = core.getTime() - var.starttime
    var.state = 'draw_rewardShort'
    return var,doo,myPoints

#Draws reward state for short verbal
def draw_rewardShort(var,doo,myPoints):
    if var.choice == 'y' or var.choice_rand == 'y':
        clock(var,doo,myPoints)
    myPoints.nowtotalUpdate(var.rewMAG) # draw the coins earned in this trial
    myPoints.totalUpdate(var.point_S) # draw the total coins earned
    var.time_coins = 'tbd' # reset var.time_coins
    time_coin = setup.mywin.flip() # show all the drawings
    start = time.clock()
    var.onset_coins = time_coin - var.starttime
    clk1 = core.CountdownTimer(var.showCoinDur)
    while clk1.getTime() > 0:
        pass
    Endpoint1 = time.clock() - start
    var.point_S+=var.rewMAG # add reward magnitude of this trial to total points earned
    myPoints.totalUpdate(var.point_S) # draw the total coins earned (new earned added)
    setup.mywin.flip() # show all the drawings (total coins updated, coins in the reward port disappeared)
    var.rew_sound.play(loops = var.rewMAG-1) # play the reward sound
    Endpoint2 = time.clock() - start
    var.coin_length = 2 # this ensures the total duration of coins is at least 2 sec.
    var.coin_dur_P = 2.2
    clk2 = core.CountdownTimer(var.coin_length-(Endpoint2-Endpoint1))
    while clk2.getTime() > 0:
        var.trial_end = core.getTime() - var.starttime
    var.state = 'none'  # return the name of next state (end of a trial)
    return var,doo,myPoints

#this function assign new stimuli positions and new rewardMag and delayMag to the yellow choice
def new_trial_setup(var,trialNum):
    var.rewmag,var.delaymag = var.bundleList_com[trialNum]
    return var

def new_trial_setup_fMRI(var,trialNum):
    var.rewmag,var.delaymag = var.bundleList_fMRI[trialNum]
    return var

#-----------------------------data recording after one trial-----------------------------------
# record all the data in this trial(learning stage 0)
#this function records all the data needed from each trial(long verbal session)
def dataRecord_longfMRI(var,p_num,expName):
    trialtime = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")# Record trialtime
    if var.choice == 'b':
        var.ychoice = 0
    elif var.choice =='y':
        var.ychoice = 1
    #sql.w_after_longfMRI(dbc,var,sessid,sd)
    var.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(expName,
                       p_num,var.trialCounter,trialtime,var.blockName,var.rewmag,var.delaymag,var.shortmag,var.shortdelay,var.choice,var.choice_rand,var.point_L,var.point_S,var.onset_jittered_fixation,var.jittered_fixation,
                       var.offset_jittered_fixation-var.onset_jittered_fixation,var.onset_decision,var.decision_RT,var.onset_confirmation,0.5,var.offset_confirmation-var.onset_confirmation,'tbd','tbd','tbd','tbd','tbd','tbd',
                       'tbd','tbd','tbd',var.press,var.trial_start,var.trial_end,var.trialCounter,var.pay,var.bluePos,var.yellowPos,var.rewMAG,var.delaymag,var.choice,var.choice_rand,var.rewmag,var.pay_delay,var.pay_num))
    var.dataFile.flush()

#long seesion data recording starts here.
def sessiondataRecord_longcom(var,p_num,expName,expDate,startt,endt):
    fileName2 = 'data/%s_%s_sessions_%s.csv' %(p_num, expName, expDate)
    with open(fileName2, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["expName","subID","starttime","endtime","num_trials","total_profit","trial_pay","pay_rew","pay_delay","sess_group"])
        writer.writerow([expName, p_num, startt, endt, var.trialCounter, var.point_L, var.pay, var.pay_num, var.pay_delay,var.runID])

#long seesion data recording starts here.
def sessiondataRecord_longfMRI(var,p_num,expName,expDate,startt,endt):
    fileName2 = 'data/%s_%s_sessions_%s.csv' %(p_num, expName, expDate)
    with open(fileName2, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["expName","subID","starttime","endtime","num_trials","total_profit","trial_pay","pay_rew","pay_delay","setlabel","runID"])
        writer.writerow([expName, p_num, startt, endt, var.trialCounter, var.point_L, var.pay, var.pay_num, var.pay_delay,var.setlabel_L,var.runID])

def dataRecord_shortfMRI(var,p_num,expName):
    trialtime = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")# Record trialtime
    if var.choice == 'b':
        var.ychoice = 0
    elif var.choice =='y':
        var.ychoice = 1
    var.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(expName,
                       p_num,var.trialCounter,trialtime,var.blockName,var.rewmag,var.delaymag,var.shortmag,var.shortdelay,var.choice,var.choice_rand,var.point_L,var.point_S,var.onset_jittered_fixation,var.jittered_fixation,
                       var.offset_jittered_fixation-var.onset_jittered_fixation,var.onset_decision,var.decision_RT,var.onset_confirmation,0.5,var.offset_confirmation-var.onset_confirmation,var.onset_clock,var.new_delayTime,
                       var.offset_clock-var.onset_clock,var.onset_coins,var.coin_dur_P,var.trial_end - var.onset_coins,var.compensation_time1,var.compensation_time2,var.time_compensation,var.press,var.trial_start,var.trial_end,
                       var.trialCounter,var.pay,var.bluePos,var.yellowPos,var.rewMAG,var.delaymag,var.choice,var.choice_rand,var.rewmag,var.pay_delay,var.pay_num))
    var.dataFile.flush()

#short session data recording strats here.
def sessiondataRecord_shortcom(var,p_num,expName,expDate,startt,endt):
    fileName3 = 'data/%s_%s_sessions_%s.csv' %(p_num, expName, expDate)
    with open(fileName3, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["expName","subID","starttime","endtime","num_trials","total_profit","sess_group"])
        writer.writerow([expName, p_num, startt, endt, var.trialCounter, var.point_S,var.runID])

#short session data recording strats here.
def sessiondataRecord_shortfMRI(var,p_num,expName,expDate,startt,endt):
    fileName3 = 'data/%s_%s_sessions_%s.csv' %(p_num, expName, expDate)
    with open(fileName3, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["expName","subID","starttime","endtime","num_trials","total_profit","setlabel","runID"])
        writer.writerow([expName, p_num, startt, endt, var.trialCounter, var.point_S,var.setlabel_S,var.runID])

# record payment information in long task
def payRecord_longfMRI(var,p_num,expName,expDate,endt,session_pay):
    fileName4 = 'data/%s_%s_payment_%s.csv' %(p_num, expName, expDate)
    print(var.pay,var.pay_num,var.pay_delay)
    with open(fileName4, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["expName","endtime","num_trials","total_profit_long","total_profit_short","trial_pay","pay_rew","pay_delay","sessionpay"])
        writer.writerow([expName, endt, var.trialCounter*2, var.point_L, var.point_S, var.pay, var.pay_num, var.pay_delay, session_pay])

def stage_instruction(stageName,var,doo):
    if var.Chinese == True:
        if stageName=='Short':
            doo.chinese_instruction.text = '短延迟阶段'
            print(stageName)
        elif stageName=='Long':
            doo.chinese_instruction.text = '长延迟阶段'
            print(stageName)
        else:
            print('no stage name')
        doo.chinese_instruction.height = 30 #30
        doo.chinese_instruction.pos=[0, 0]
        doo.chinese_instruction.draw()
    else:
        doo.instruction.text = format_text(str(stageName)+' Delays Stage')
        doo.instruction.height = 30 #30
        doo.instruction.pos=[0, 0]
        doo.instruction.draw()
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    clk = core.CountdownTimer(2.5)
    while clk.getTime() > 0:
        pass

# show all the big coins at the end of a session/block
def show_bigCoins(var,myPoints):
    myPoints.stackAllbig(var.points) # draw all the big coins
    setup.mywin.mouseVisible = False
    setup.mywin.flip() # show the drawings
    clk = core.CountdownTimer(2)
    while clk.getTime() > 0:
        pass # keep the drawings for 2 seconds
    var.dataFile.close() # close the data file


# get the total points and trial number of this stage
def total_Points_trialCounter(var):
    return var.points, var.trialCounter

# reset the total points and trial number to 0
def reset_Points_trialCounter(var):
    var.trialCounter = 0
    var.points = 0
    var.totalTrialCounter = 0

#  shows all the coins earned at the end of all learning stages
def show_bigCoins_total(totalProfits,myPoints):
    myPoints.stackAllbig(totalProfits) # draw all the big coins
    setup.mywin.mouseVisible = False
    setup.mywin.flip() # show the drawings
    clk = core.CountdownTimer(2)
    while clk.getTime() > 0:
        pass # keep the drawings on the screen for 2 seconds

# generate the end session instruction for verbal stage
#def end_instruction(doo,trial_pay,session_pay,pay_num,pay_delay,var):
#    if not var.Chinese:
#        doo.instruction.text = u'This is the end of the experimental session.\n\nTrial # %r from Long Delays Stage # %r was randomly chosen to pay you.\n\nYour choice in that trial was: %r coin(s) in %r days.\n\nPlease report to the experimenter. Thank you very much for your participation!' % (trial_pay,session_pay,pay_num,pay_delay)
#        doo.instruction.pos=[0,0]
#        doo.instruction.height = 30
#        doo.instruction.draw()
#    else:
#        doo.chinese_instruction.text = u'本轮实验结束.\n\n系统随机选择了第 %r个<长时延迟阶段>的第 %r号实验进行支付\n\n您在该次实验的选择是: 在 %r天后获得 %r 金币.\n\n请向实验员报告. 非常感谢您前来参与本次实验!'% (session_pay,trial_pay,pay_delay,pay_num)
#        doo.chinese_instruction.pos=[0,0]
#        doo.chinese_instruction.height = 30
#        doo.chinese_instruction.draw()
#    setup.mywin.flip()
#    clk = core.CountdownTimer(15)
#    while clk.getTime() > 0:
#        pass

def end_instruction(var,doo):
    if var.Chinese:
        doo.chinese_instruction.text = '本阶段实验结束'
        doo.chinese_instruction.pos = [0,0]
        doo.chinese_instruction.draw()
    else:
        doo.instruction.text = 'This is the end of experiment'
        doo.instruction.pos = [0,0]
        doo.instruction.draw()
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    clk = core.CountdownTimer(5)
    while clk.getTime() > 0:
        pass

def block_break(var,doo):
    if var.Chinese:
        doo.chinese_instruction.text = '请休息 %r 秒.\n\n或者您可以按下‘ENTER’直接进入下一模块.'% var.blockBreak
        doo.chinese_instruction.pos=[0,0]
        doo.chinese_instruction.height = 30
    else:
        doo.instruction.text = 'Please take a %r-second break.\n\nPress enter to stop the break and you will continue to the next block.' % var.blockBreak
        doo.instruction.pos=[0,0]
        doo.instruction.height = 30
    delayStart = core.getTime()
    delayEnd = core.getTime()
    while delayEnd-delayStart<=var.blockBreak:
        var.secPos2 = 'TBD'
        var.secPos = np.floor(delayEnd-delayStart+60-var.oneRound)*360/60#NB floor will round down to previous second
        if not event.getKeys(keyList = "return"):
            if var.secPos != var.secPos2:
                delayCircle(var,doo)
                scales(var,doo)
                doo.clock.visibleWedge = (0, var.secPos*(60/var.blockBreak)+1)
                doo.clock.draw()
                scales(var,doo)
                if var.Chinese:
                    doo.chinese_instruction.draw()
                else:
                    doo.instruction.draw()
                setup.mywin.mouseVisible = False
                setup.mywin.flip()
            var.secPos2 = copy.copy(var.secPos)
            delayEnd = core.getTime()
        else:
            breakCancel = core.getTime()
            var.blockBreakCancel = breakCancel-delayStart
            break
    delayCircleEmpty(var,doo)
    scales(var,doo)
    if var.Chinese:
        doo.chinese_instruction.draw()
    else:
        doo.instruction.draw()
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    clk = core.CountdownTimer(0.2)
    while clk.getTime() > 0:
        pass

# this function randomly picks a trial from all long verbal trials to pay the subjects
def pick_pay(pick1,pick2):
    pay_session = random.choice([1,2])
    #print(pay_session)
    if pay_session == 1:
        #print(pay_session,pick1)
        return pay_session,pick1
    else:
        #print(pay_session,pick2)
        return pay_session,pick2

# this funcion assigns the final payment given the session selected to pay
def assign_pay(session_pay,pay_delay1,pay_delay2,pay_num1,pay_num2):
    if session_pay == 1:
        #print(pay_delay1, pay_num1)
        return pay_delay1, pay_num1
    else:
        #print(pay_delay2, pay_num2)
        return pay_delay2, pay_num2

# this function formats text to be center aligned
def format_text(text):
    text = text.splitlines()
    length = 0
    for i in range(len(text)):
        if len(text[i]) > length:
            length = len(text[i])
    text2 = ''
    for i in range(len(text)):
        text2 = text2 + '\n' + text[i].center(length)
    #print text2 # does it work?
    return text2

#This function prepares end information
def end_block(var,doo):
    if var.Chinese:
        doo.chinese_instruction.text = '    本阶段结束 \n\n请保持头部不动'
        doo.chinese_instruction.pos = [0,0]
        doo.chinese_instruction.draw()
    else:
        doo.instruction.text = 'This is the end of this stage \n\n Please keep head still'
        doo.instruction.height = 30
        doo.instruction.pos = [0,0]
        doo.instruction.draw()
    setup.mywin.mouseVisible = False
    setup.mywin.flip()
    clk = core.CountdownTimer(5)
    while clk.getTime() > 0:
        pass
#-------------------Function Name Dictionary(for recursive state calling)------------------------
funcDic = {'draw_init':draw_init,'wait_for_choice':wait_for_choice,'draw_reward':draw_reward,'draw_rewardShort':draw_rewardShort}
funcDic_behavior = {'draw_init':draw_init,'wait_for_choice_behavior':wait_for_choice_behavior,'draw_reward_behavior':draw_reward_behavior,'draw_rewardShort':draw_rewardShort}
