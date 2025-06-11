# fMRI Experiment Pipeline

- Total subject number invited to fMRI task: 40 
- Start date: Oct 2019 

## Computer Session
Subjects completed one behavioral task (~1 hour) on a Dell laptop. 
Some adjustments to the computer session were made according to the COVID risk minimization plan (sanitized pens, sanitizer, extra masks).

### Before an experiment session
- Check subjid is in the dtb;
- Subject_info.csv file should be manually filled in on the laptop (columns 'netid',	'group',	'set',	'zoomed-in L',	'zoomed-in S';
- Experimenter prepares (and sanitizes) laptop’s touchpad, mouse, and headphones.

### During the session
As per the COVID risk minimization plan:
- The experimenter wears a mask at all times and asks the participant to wear a mask as well.
- The experimenter needs to keep a distance of 1-2m from the participant, so the experimenter needs to prepare forms and place them near the computer and open necessary tabs/windows in advance on the laptop. If possible, the experimenter needs to guide the participant on what form to fill in from a distance, but the experimenter should definitely help the participant run python from CMD (Git CMD) for sound check and the task script.

- Participant signs two copies of Consent form: one stays with the experimenter, the other should be given to the participant.
- Participant fills in the 3T form - if any concerns with fMRI, the participant does not qualify for the study.
- Participant fills in the Economic Experiment Survey following the google form link.
- Participant watches the video for instructions: instructions.mp4 (audio was generated via Baidu's text-to-speech API).
- The experimenter helps the participant to check the sound;
- The experimenter helps participant to start task code by running `python <task_script.py>` ('_odd' for odd subjid and '_even' for even subjid) and instructs participant from the distance to press tab twice to enter subjid (subjid=netid for fMRI study) and input '1' for the run number.
- Participant fills in the feedback survey using the google form link.
- The experimenter calculates the payment. 
- The experimenter pays the participant via Alipay or WeChat: the total amount is added to the schedule google spreadsheet, only the amount due today is paid, the delayed amount is scheduled to be paid after the delay in days. Exchange rate: 20 + 0.02xtotal_short + 2xchosentrial_long

**After the session** the experimenter sanitizes laptop’s touchpad, mouse and headphones again.

### After the completion of experiments
1. Run `rewdelsensitivity.m`, and check criteriapass. If 'pass all' is 6, invite the participant to the fMRI session.
3. Schedule a session at the fMRI facility, give the subject an fMRI_ID. 

## fMRI Session
Subjects will complete this session (~1.5 hours) on the Dell laptop labelled 'fMRI' in the fMRI facility (华东师范大学（中山北路校区认知神经科学研究所)).

### Before an experiment session
1. Prescreen subjects verbally based on the 3T MRI security form: metal implants, pregnancy, etc. Remind subjects not to wear metallic clothing, excessive jewelry or makeup (including some contact lenses). Suggest comfortable clothing for lying down for at least 45 mins. Belts are allowed and can be removed on site. Vision correction can be handled on site.
2. Check and bring to the facility CD bag, laptop charger, adaptor HDMI-VGA, VGA cable, thinner foam (for head fixation).
3. Check and bring the screening form (empty) and the compensation sheet.
4. Find and bring the consent (signed at the behavioral computer session) for that particular subject.

### fMRI scanning setup

1. Sequence: delay_final_erlichlab_sequence;
2. Settings: set tilt angle to -30 ° in task scanning period (EPI period);
3. Connect the charger to the laptop;
4. Connect cables to the laptop: display cable, sound cable, 5-finger response box USB cable.
 
**Remember**: **USE 1024 x 768 resolution for external display!!**

### During an experiment session

1. Ask the participant to fill in and check the 3T MRI security form.
2. Play video instructions.mp4 and **AGAIN REMIND** subject to make choices in a timely manner.
3. Prepare MR-compatible glasses (if needed). 
4. Remove forbidden items (including any cards, which will be erased in the magnetic field) and enter into the fMRI room. 
5. Use the 20-channel headset (for headphones). 
6. Use the 5-finger button box (index finger presses '1' for left choice and middle finger presses '2' for right choice). 
7. Fix the subject's head using foam. 
8. **Important:** Remind subjects not to move their head inside the scanner during the task.
9. Check sound by running `python coinsoundtest.py` (set volume to 35 before the test; do the sound check **each time** after connecting the cables and situating the subject in the scanner room);
10. Start code by running `python <script.py>` (setgroup 1,3  are SL-LS-SL-LS, set group 2,4 are LS-SL-LS-SL), input subjid, run ID, **move mouse downwards (so the curser is hidden)**, wait for trigger, when fMRI scanning is ready, press the synchronization button (同步复位), then the technician starts scanning. Note: when you press the synchronization button on the response system, then an indicator light will turn green, then when the scanner gives a pulse, it goes out;
11. Pay attention to what shows up on the screen. If the subject fails to make a choice on several runs, talk to the subject in between the runs. Unexpected things may happen. Time each run roughly from the trigger pulse. **Log the unexpected things (subjid, run #, time from the run onset / trigger pulse, what happened).**
12. Pay attention to when the runs end. Once a run finishes, let the technician know to stop scanning.
13. Ask subjects how they are feeling after each run. Ask the subject if they need to rest for some time after two runs.
14. Repeat steps 10-13 for three more times (total number of runs = 4).
15. Calculate payment. To balance payment between short and long tasks, only reward < 20 in the long task will be picked as the final reward.
16. After the fMRI session, if the participant has any feedback, ask them to write it down in a blank file within the Feedback_fMRI folder.
17. Save fMRI data to CDs, write on the CD 'date' and 'subjid'.

Compensation:
According to IRB approval, compensation is calculated as below, automatically, using python script.
(1) Behavioural: 20 + 0.02 × Short + 2 × Long RMB
(~40-68 RMB)
(2) fMRI: 100 + 0.02 × Short + 2 × Long RMB  
(~140-158 RMB)

## Dell laptop PsychoPy3 setup
PsychoPy 3.1.5 installed in `C:\Program Files (x64)\PsychoPy3` on laptop labelled 'fMRI'
