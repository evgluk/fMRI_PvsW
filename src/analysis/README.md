# Analysis Pipeline
(1) Behavioral data events are organized as BIDS;

(2) Raw dicom data is converted into [BIDS](http://bids.neuroimaging.io/) format by [dcm2bids](https://github.com/cbedetti/Dcm2Bids) and validated; 

(3) BIDS data quality control is done;

(4) BIDS data preprocessing follows fmriprep pipeline;

(5) Main analysis as in pre-registration includes:
- GLMs + ROI
- RSA
- SVM

## 1. Behavioral data organization
Behavioral data was collected in two sessions: computer session and fMRI session. 
In this project, behavioral data were recorded as csv files locally on Dell laptops and then moved to the DTB. 

After data was uploaded to DTB, the subjid, the fMRI id and BIDS id of the current subject were matched. Then ran in bash `python3 createbids_beh.py` to add BIDS events files. 

The output included 10 columns:
- onset            ---> the onset of the event；
- duration         ---> the duration of the event；
- event_type       ---> event type, Decision, Confirmation, Decision_end (from the onset of decision until the end of that trial) and Confirmation_end (from the onset of confirmation until the end of that trial)；
- trial_type       ---> LongDelay_Behavior or ShortDelay_Behavior；
- delayed_reward   ---> rewmag of the delayed option；
- delaytime        ---> delay time of the delayed option；
- choice           ---> decison on current trial, 0--now, 1--delay, n/a--no press；
- outcome_mag      ---> reward magnitude of the chosen option, if no response on current trial, then this is decided by the computer-picked choice, and the same below;
- outcome_delay    ---> delay of the chosen option；
- subjective_value ---> subjective value of the delayed option.

