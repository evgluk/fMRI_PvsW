# fMRI Experiment Pipeline

- Planned subject number: 40 (total subject number invited to fMRI task)
- Start date: Aug 2019 (new pilots testing behavioral criteria from May 2019)

## Behavior Session
Subjects completed one behavioral task (~1 hour) on a Dell laptop. 
Some adjustments to computing session were made according to the COVID risk minimization plan (sanitized pens, sanitizer, extra masks).

### Before an experiment session
- Check subjid is in the dtb;
- Subject_info.csv file should be manually filled on experiment computer (columns 'netid',	'group',	'set',	'zoomed-in L',	'zoomed-in S';
- Experimenter prepares (and sanitizes) laptop’s touchpad, mouse, and headphones.

### During the session
As per the COVID risk minimization plan:
- Experimenter wears a mask at all times and asks participant to wear a mask as well.
- Experimenter needs to keep distance 1-2m from participant, so experimenter needs to prepare forms and place them near the computer and to open necessary tabs/windows in advance on the laptop. If possible experimenter needs to guide participant on what form to fill in from distance, but experimenter should definitely help participant run python from CMD (Git CMD) for sound check and the task script.

- Participant signs two copies of Consent form: one stays with the experimenter, the other should be given to subject.
- Participant fills in 3T form - if any concerns with fMRI, participant does not qualify for the study.
- Participant fills in the Economic Experiment Survey following the google form link.
- Participant watches the video for instructions: instructions.mp4 (audio was generated via Baidu's text-to-speech API).
- Experimenter helps participant to check sound;
- Experimenter helps participant to start task code by running `python <task_script.py>` ('_odd' for odd subjid and '_even' for even subjid) and instructs participant from the distance to press tab twice to enter subjid (subjid=netid for fMRI study) and input '1' for the run number.
- Participant fills in the feedback survey, following the google form link.
- Experimenter calculates the payment. 
- Experimenter pays participant via Alipay or WeChat: total amount is added to the schedule google spreadsheet, only amount due today is paid, the delayed amount is scheduled to be paid after the delay in days. Exchange rate: 20 + 0.02xtotal_short + 2xchosentrial_long

**After the session** experimenter sanitizes laptop’s touchpad, mouse and headphones again.

### After completion of experiments
1. Run `rewdelsensitivity.m`, and check criteriapass. If pass all is 6, invite subject to fMRI.
3. Schedule session at fMRI facility, give the subject an fMRI ID. 

## fMRI Session
Subjects will complete this session (~1.5 hours) on the Dell laptop labelled 'fMRI' in fMRI facility (华东师范大学（中山北路校区认知神经科学研究所)).

### Before an experiment session
1. Prescreen subjects verbally based on 3T MRI security form: metal implants, pregnancy, etc. Remind subjects not to wear metallic clothing, excessive jewelry or makeup (including some contact lenses). Suggest comfortable clothing for lying down for at least 45 mins. Belts are allowed and can be removed on site. Vision correction can be handled on site.
2. Check and bring to the facility CD bag, laptop charger, adaptor HDMI-VGA, VGA cable, thinner foam (for head fixation).
3. Check and bring screening form (empty) and compensation sheet.
4. Find and bring the consent (signed at behavioral computer session) for that particular subject.

### fMRI scanning setup

1. Sequence: delay_final_erlichlab_sequence;
2. Settings: set tilt angle to -30 ° in task scanning period (EPI period);
3. Connect charger to the laptop;
4. Connect cables to the laptop: display cable, sound cable, 5-finger response box USB cable.
 
**Remember**: **USE 1024 x 768 resolution for external display!!**

### During an experiment session

1. Ask the participant to fill in and check the 3T MRI security form.
2. Play video instructions.mp4 and **AGAIN REMIND** subject to make choices in a timely manner.
3. Prepare MR-compatible glasses (if needed). 
4. Remove forbidden items (including any cards, which will be erased in magnetic field) and enter into the fMRI room. 
5. Use the 20-channel headset (for headphones). 
6. Use 5-finger button box (index finger presses '1' for left choice and middle finger presses '2' for right choice). 
7. Fix the subject's head using foam. 
8. **Important:** Remind subjects not to move head inside scanner during task.
9. Check sound by running `python coinsoundtest.py` (set volume to 35 before the test; do the sound check **each time** after connecting the cables and situating subject in the scanner room);
10. Start code by running `python <script.py>` (setgroup 1,3  are SL-LS-SL-LS, set group 2,4 are LS-SL-LS-SL), input subjid, run ID, **move mouse downwards (so the curser is hidden)**, wait for trigger, when fMRI scanning is ready, press the synchronization button (同步复位), then the technician starts scanning. Note: when you press the synchronization button on response system, then an indicator light will turn green, then when scanner gives a pulse, it goes out;
11. Pay attention to what shows up on the screen. If subject fails to make a choice on several runs, talk to the subject in between the runs. Unexpected things may happen. Time each run roughly from the trigger pulse. **Log the unexpected things (subjid, run #, time from the run onset / trigger pulse, what happened).**
12. Pay attention to when the runs end. Once a run finishes, let technician know to stop scanning.
13. Ask subjects how they are feeling after each run. Ask subject if they need to rest for some time after two runs.
14. Repeat steps 10-13 for three more times (total number of runs = 4).
15. Calculate payment. To balance payment between short and long task, only reward < 20 in long task will be picked as final reward.
16. After fMRI session, if participant has any feedback, ask them to write down in a blank file within Feedback_fMRI folder .
17. Save fMRI data to CDs, write on the CD 'date' and 'subjid'

Compensation:
According to IRB approval, compensation is calculated as below, automatically, using python script above
(1) Behavioural: 20 + 0.02 × Short + 2 × Long RMB
(~40-68 RMB)
(2) fMRI: 100 + 0.02 × Short + 2 × Long RMB  
(~140-158 RMB)

### After an fMRI experiment session
Convert fMRI data by running dicom.exe (~5 mins for one participant data) on fMRI laptop. 

## Recorded fMRI Data (in csv) and uploaded to dtb afterwards
        expName: name of task: ShortDelay_fMRI or LongDelay_fMRI
        p_num: subject ID
        trialnum: trial number
        trialtime: timestamp of each trial onset
        rewmag: delayed reward amount
        delay: delay time
        smag: now reward
        sdelay: 0
        choice: The picked option, b = blue, y = yellow  
        choice_rand: if no choice made by subject, a random option will be picked as choice
        point_L: total reward amount in long stage in current block (start from 0 again in next block)
        point_S: total reward amount in short stage in current block (start from 0 again in next block)

- The data below are variables saved in json format in the trialdata variable, including timing and trial setting information:

        j_onset_jittered_fixation: timestamp of jittered fixation onset
        j_duration_jittered_fixation_P: planned duration of fixation
        j_duration_jittered_fixation_A: actual duration of fixation
        j_onset_decision: timestamp of decision phase onset
        j_decision_RT: reaction time in decision phase
        j_onset_confirmation: timestamp of confirmation phase onset
        j_duration_confirmation_P: planned duration of confirmation phase
        j_duration_confirmation_A: actual duration of confirmation phase
        j_onset_clock: timestamp of  onset
        j_duration_clock_P: planned duration of clock phase
        j_duration_clock_A: actual duration of clock phase
        j_onset_coins: timestamp of coins phase onset
        j_duration_coins_P: planned duration of coins phase
        j_duration_coins_A: actual duration of coins phase
        j_compensation_start: timestamp of compensation onset, to caculate time compensation in clock phase
        j_compensation_end: timestamp of compensation offset
        j_time_compensation: compensated time in clock phase (due to confirmation and other time)
        j_press: if subject press to make choice or not
        j_trial_start: timestamp of trial onset
        j_trial_end: timestamp of trial offset
        j_trial: trial number
        j_trial_pay: which trial to be paid as reward in long stage
        j_BluePos: blue reward position
        j_yellowPos: yellow reward position
        j_rewMag: reward mag of chosen option
        j_delay: delay time in current trial
        j_choice: the option picked by subject
        j_choice_rand: the randomly picked option
        j_yellowRew: yellow reward
        j_pay_delay: delay time of the chosen trial in long stage (to pay subject)
        j_pay_num: reward mag of the chosen trial in long stage (to pay subject)


## Dell laptop PsychoPy3 setup
PsychoPy 3.1.5 installed in `C:\Program Files (x64)\PsychoPy3` on laptop labelled 'fMRI'
