# TODO
* [ ] 


# fMRI Experiment Pipeline

- Planned subject number: 40 (total subject number invited to fMRI task)
- Start date: Aug 2019 (new pilots testing behavioral criteria from May 2019)
- Participant recruitment [New Link Since 2019 September](https://nyu.qualtrics.com/jfe/form/SV_eCBeLJAxSGIi87j) currently owned by Chloe.
  ([Old link still in use on the flyer as of 2019 November](https://nyu.qualtrics.com/jfe/form/SV_88ENhyJPrOk6NIV))
- Participant information and date: [fMRI Schedule 2019](https://docs.google.com/spreadsheets/d/1jYnryyazLO8a_ZfNjLjKABDQpUbPC7WcQCLOPonGU20/edit#gid=0)

## Behavior Session
Subjects will complete one behavioral task (~1 hour)  on Dell laptop with label '1' (at NYUSH, Pudong) or '3' (at ECNU). 

The plan for the computer session is adjusted according to the COVID risk minimization plan.

### Before an experiment session
- Check subjid is in the dtb;
- Subject_info.csv should be manually filled on experiment computer and git committed (@温轩 we didn't try git commit, we can try it on Wednesday); git pull
- Experimenter prepares at least 2 pens (one sanitized for participant), subject’s ‘subjid’ written on the paper (for subject to input later), 2 copies of Consent Form, 3T form and subject payment form (Jenya prints necessary documents, when experimenter notifies Jenya if some of the forms are missing)
- Experimenter prepares sanitizer and extra masks for participants, sanitizes laptop’s touchpad, mouse and headphones.

### During the session:
- Experimenter wears a mask at all times and asks participant to wear a mask as well.
- Experimenter needs to keep distance 1-2m from participant, so experimenter needs to prepare forms and place them near the computer and to open necessary tabs/windows in advance on the laptop. If possible experimenter needs to guide participant on what form to fill in from distance, but experimenter should definitely help participant run python from CMD (Git CMD) for sound check and the task script.
- Participant signs two copies of Consent form: one stays with the experimenter, the other should be given to subject.
- Participant fills in 3T form - if any concerns with fMRI, participant does not qualify for the study.
- Participant fills in the Economic Experiment Survey following the google form link (in the Code/README): [version for subjects](https://docs.google.com/forms/d/e/1FAIpQLSdSk8AqXYcG9T06muwiTaEnw3c3Dav6vUDxWQdZlXEvOFfvXA/viewform) and [version to edit](https://docs.google.com/forms/d/1fxkDqfSHgh7O_-vNsFZ4i7p7sgCj161wTxRBfmQl5Q4/edit)
- Participant watches the video for instructions: instructions.mp4 (audio was generated via Baidu's text-to-speech API).
- Experimenter helps participant to check sound by running `python coinsoundtest.py`
- Experimenter helps participant to start task code by running `python <task_script.py>` (‘_odd’ for odd subjid and ‘_even’ for even subjid) and instructs participant from the distance to press tab twice to enter subjid (subjid=netid for fMRI study) and input ’1’ for the run number.
- Participant fills in the feedback survey, following the google form link (in the Code/README): [version for subjects](https://docs.google.com/forms/d/e/1FAIpQLSdjX0ycAdDlcZKNHH8l1y9b-n_Sak-nQEfWHWGLT4xrwAW5eA/viewform) and [version to edit](https://docs.google.com/forms/d/1SirgZCLb-LiTtki8HMGbY6oygZN__PzErbAIy_Xt0r8/edit)
- Experimenter calculates the payment from Code/data/Behavior_combined_(odd)|(even).csv 
- Experimenter pays participant via Alipay or WeChat: total amount is added to the schedule google spreadsheet, only amount due today is paid, the delayed amount is scheduled to be paid after the delay in days. Exchange rate: 20 + 0.02xtotal_short + 2xchosentrial_long

**After the session** experimenter sanitizes laptop’s touchpad, mouse and headphones again.

### After completion of experiments
1. Upload data to ino by running `./move_and_upload_behavioral_data.sh` on Dell laptop in bash.
2. SSH into ino, start matlab and run `rewdelsensitivity.m`  (in fMRI_delay/Analysis), and check criteriapass. If pass all is 6, invite subject to fMRI.
3. Schedule session at fMRI facility give subject fMRI ID. Contact scheduler (WeChat ID: wzcRib241). Send schedule for next month around 20th. Give fMRI ID base on the order of experiment time.

## fMRI Session
Subjects will complete this session (~1.5 hours) on the Dell laptop labelled 'fMRI' in fMRI facility (华东师范大学（中山北路校区认知神经科学研究所)).

### Before an experiment session
1. Prescreen subjects verbally based on 3T MRI security form: metal implants, pregnancy, etc. Remind subjects not to wear metallic clothing, excessive jewelry or makeup (including some contact lens). Suggest comfortable clothing for lying down during at least 45 mins. Belts are allowed and can be removed on site. Vision-correction can be handled on site.
2. Ensure Windows updates, if any, are installed so that they don't show up during experiments. The automatic update is turned off.
3. Check and bring to the facility CD bag, laptop charger, adaptor HDMI-VGA, VGA cable, thinner foam (for head fixation).
4. Check and bring screening form (empty) and compensation sheet (payment form, 024-2017).
5. Find and bring the consent (signed at behavioral computer session) for that particular subject.

### fMRI scanning setup

1. Sequence: select Tongrui/erlich_NYU/delay_final_erlichlab_new (two images from `img/` should appear below)
![](img/sequence1.jpg)
![](img/sequence2.jpg)
2. Settings: set tilt angle to -30 ° in task scanning period (EPI period). Note: the example picture does not have frontal lobe completely covered, but actual setup will do. (one image from `img/` should appear below)
![](img/tilt_angle.jpg)
3. Connect charger to the laptop
4. Connect cables to the laptop: display cable, sound cable, 5-finger response box USB cable (one image from `img/` should appear below)
 
**Remember**: 
 - cables: i) connect laptop with the cable of 5-finger response box, the 2-finger response box has trouble in sending signal back to laptop; ii) ask technician to use “sound+image” cable to link laptop to their projector, another cable can’t transmit sound stimulus to headphone
 - **USE 1024 x 768 resolution for external display!!**
 - if there is a problem with projecting the laptop display: i) ensure that computer power setting is on 'balanced'; ii) fMRI laptop display refresh rate is 60Hz; iii) move the switch 'right' for external display; iv) check the display setting on the stationary desktop computer.
![](img/cable.jpg)
![](img/external_display_resolution.jpg)
![](img/dell_laptop_power_setting.png)
![](img/dell_laptop_display_refresh_rate.png)
![](img/stationary_desktop_screen_settings.jpg)

### During an experiment session

1. Ask participant to fill in and check 3T MRI security form.
2. Play video instructions.mp4 and **AGAIN REMIND** subject to make choices in a timely manner.
3. Prepare MR-compatible glasses (if needed). 
4. Remove forbidden items (including any cards, which will be erased in magnetic field) and enter into the fMRI room. 
5. Use the 20-channel headset (for headphones) 
6. Use 5-finger button box (index finger presses '1' for left choice and middle finger presses '2' for right choice). 
7. Fix the subject's head using foam (if fMRI facility foam is too thick, use ours). 
8. **Important:** Remind subjects not to move head inside scanner during task.
9. Check sound by running `python coinsoundtest.py` (set volume to 35 before the test; do the sound check **each time** after connecting the cables and situating subject in the scanner room);
10. Start code by running `python <script.py>` (setgroup 1,3  are SL-LS-SL-LS, set group 2,4 are LS-SL-LS-SL), input subjid, run ID, **move mouse downwards (so it's captured by the screen frame)**, wait for trigger, when fMRI scanning is ready, press the synchronization button (同步复位), then the technician starts scanning![](img/synchronization_button.jpg) Note: when you press the synchronization button on response system, then an indicate light will turn green, then when scanner gives a pulse, it goes out;
11. Pay attention to what shows up on the screen. If subject fails to make a choice on several runs, talk to the subject in between the runs. **!!!! Absolutely no divided attention: no laptop/phone playing, checking mail, code, etc.** Unexpected things may happen. Time each run roughly from the trigger pusle. **Log the unexpected things (subjid, run #, time from the run onset / trigger pulse, what happened).**
12. Pay attention to when the runs end. Once a run finishes, let technician know to stop scanning.
13. Ask subjects how they are feeling after each run. Ask subject if they need to rest for some time after two runs.
14. Repeat steps 10-13 for three more times (total number of runs = 4).
15. Calculate payment by running `python fMRI_payment.py` (creates a payment.csv file to upload to dtb). To balance payment between short and long task, only reward < 20 in long task will be picked as final reward.
16. After fMRI session, if participant has any feedback, ask them to write down in a blank file within Feedback_fMRI folder in the 'repos/fMRI_delay'.
17. Save fMRI data to CDs, write on the CD 'date' 'subjid'

Compensation:
According to IRB approval, compensation is calculated as below, automatically, using python script above
(1) Behavioural: 20 + 0.02 × Short + 2 × Long RMB
(~40-68 RMB)
(2) fMRI: 100 + 0.02 × Short + 2 × Long RMB  
(~140-158 RMB)

### After an fMRI experiment session

1. upload behavioral data for fMRI session by running `./move_and_upload_behavioral_data.sh` on the Dell laptop in bash, convert fMRI data by running dicom.exe (~5 mins for one participant data) on fMRI laptop (don't forget to remove subject's names and keep their fMRI subject IDs, details and further data convertion in 'Analysis/README.md'. 

# Appendix
## Upload Behavioral Data to DTB

run `./move_and_upload_behavioral_data.sh` in Git Bash on Dell laptops.

If not completed successfully (log errors), check whether the data is uploaed to ino then run on ino `python3 upload_behavioral_data.py -t client`

* Please check working directory setting before use;
* Please check whether Code/Subject_info.csv is up-to-date;
* JSON data are also saved per each trial, here is the json variable list: 
    * trial,trial_pay, BluePos, yellowPos,rewMag,delay,choice,
  choice_rand,yellowRew,point_L,point_S,pay_delay, pay_num,onset_ITI_1st,duration_ITI_1st_A,onset_decision,decision_RT, onset_ITI_2nd,
  duration_ITI_2nd_A,onset_clock, duration_clock_A,onset_confirmation, duration_confirmation_A,onset_coin, duration_coin_A,time_compensation;
    * "_A" here stands for "Actual", i.e., time lag may exist in some time duration, and we only record actual time data (time durations as planned are with "_P" in original datafile);
    * In JSON data, "choice" always contains chosed option rather than none, if subject misses, then computer-chosed option will be filled. "Choice_rand" is what computer chooses on that trial.

**In fMRI trials, stage is always "1" because fMRI blocks are ran seperately, thus stage won't automatically add 1 after completion of previous block;**


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
1. Git for Windows (2.24.0 , 64-bit) is installed in `C:\Program Files\Git`, which bundles Git Bash
  1. Git bash important env variables: `OSTYPE=msys`, `HOME=/c/Users/user`
2. PsychoPy 3.1.5 installed in `C:\Program Files (x64)\PsychoPy3` on laptop labelled 'fMRI', in `C:\Users\user\AppData\Local\Psychopy3` on laptop labelled '1'.
3. A python virtual environment was created for fMRI_delay via
```bash
/path/to/psychop3/python -m venv --system-site-packages venv_fMRI_delay
```
4. The following was written to `.bash_profile` in the home directory such that Git Bash on startup will activate the virtual environment (to deactivate, run `deactivate` in bash)
```bash
cd ~/repos
source venv_fMRI_delay/Scripts/activate
```
5. python points to duplicated PsychoPy3's python interpreter, so the task code can be started by `python <task_script.py>` in bash

## Mean compensation level calculation, change implemented
Due to new Broad sets of long short
Short delay rewmag (100 trials) min=400 max=980 mean=690 (for a 50-50 subject)
Long delay rewmag range min=4 max=15 mean=7.18 (for a 50-50 subject)

1. Behavior
  * Old: 20 + 0.05xshort + 4xlong: min=56 max=129 mean=83.2 mean compensation level 166.4 RMB/hour
  * New: 20 + 0.02xshort + 2xlong: min=36 max=69.6 mean=48.2 mean compensation level 96.4 RMB/hour
2. fMRI
  * New: 100 + 0.02xshort + 2xlong: min=116 max=149.6 mean=128.2 mean compensation level 128.2 RMB/hour

## baidu_tts.py 
(requires mutagen and baidu-aip) generates instructions_audio.mp3 and instructions_audio.srt (substitles) from Chinese_instructions_for_participants.txt. 
Usage: ./baidu_tts.py 
