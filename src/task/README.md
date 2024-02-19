[email *jlukinova@nyu.edu* for further explanations]
## Necessary setups before intertemporal choice experiment

**Computer setup:**

    1. Python 2.7 needs to be installed in your computer
    2. Download and install PsychoPy 1.83.04
    3. Download and install any MySQL user interface
    4. git clone repos/ folder (with helpers/ folder and code/ folder in it)
    'helpers' is custom module needed to access dtb
    5. Setup working path
        - In repos/code/functions.py, find setpath() function
        - sys.path.append('directory where you git cloned repos folder')
        - sys.path.append('directory where your /Python/2.7/site-packages is')
    6. Setup MySQL database
        6.1. Setup all tables(and column names) needed in our code
            -sessions: sessid/subjid/sessiondate/starttime/treatment/hostip/settingsid/startts
            -sessions_end: sessid/subjid/sessiondate/endtime/treatment/hostip/num_trials/total_profit/settingsid/sessionpay/trialpay/payrew/paydelay/endts/moneyscarcity/timescarcity/hurry/questionnaire
            -settings: settingid/expgroupid/data/description
            -subjinfo: subjid/netid/firstname/fullname
            -trials: trialid/sessid/trialtime/trialnum/trialdata/stage/rewmag/delay/choice/points/smag/sdelay/short_delay/long_delay
        6.2. Set database user name
            - In repos/code/functions, find dbconnect() function
            - Input your database user name in sql.select_user(dbc,'your user name')
        6.3. Setup a subjects pool in your database
            - In 'subjinfo' table, input information of all subjects
            - There needs to be an ID(netid) for each subject to input at the beginning of each program that will lead a unique subjid saved in the 'subjinfo' table
        6.4. Create two necessary settings
            - You can input whatever fits your need in the n/a's 
            - In 'settings' table, create two rows of necessary settings for our experiment:
| settingsid | expgroupid | data                                                                                                                             | description |
|-----------:|------------|----------------------------------------------------------------------------------------------------------------------------------|-------------|
| n/a        | n/a        | {"delay": [ 3 , 7, 14, 30, 64], "refresherNum": 10, "blockTrial": 2, "passThreshold": 2, "rewdelpair": 10, "ddiscounter": 1.2} | time_delay    |            

**Subject data saving preparation**
    
    1. Once the subject gave his consent, add his data to subjinfo table and he will be given a subjid (manual entry in the dtb).
    2. Participant will be instructed to insert his netID (linked to subjid). If netID is not in the database, PsychoPy will display an error message.

**Run the following code:**

    1. For [subjects with odd subjid] verbal blocks -> run verbal_combined_odd.py
    2. For [subjects with even subjid] verbal blocks -> run verbal_combined_even.py

**Auxiliary files catalog**
    
    1. functions.py: file which contains all functions needed for other scripts
    2. SQL_call.py: all database related commands(read and write) needed for other scripts
    3. Short_Verbal.py: short-delay session in verbal experiment (imported by verbal_combined_odd/even.py)
    4. Long_verbal.py: long-delay session in verbal experiment (imported by verbal_combined_odd/even.py)
    5. doodle.py: defines class Doodle which creates circle/text/sound objects and modifies their properties (important file that decreases memory use)
    6. newPoints.py: defines class NewPoins which creates coin objects and modifies their properties (imported by all files that need to draw coins)
    7. setup.py: defines the window that displays stimuli and other setups (imported by all files for experiments)
    8. variables.py: defines class Variables which defines all the variables needed (imported by all files for experiments)
    9. coin_echo5.wav: the sound stimuli when getting a coin
    
## Necessary setups before timing experiment

**Computer setup:**

    1. Python 2.7 needs to be installed in your computer
    2. Download and install PsychoPy 1.83.04
    3. git clone repos/ folder 
    4. Setup working path
        - In repos/code/functions.py, find setpath() function
        - sys.path.append('directory where you git cloned repos folder')
        - sys.path.append('directory where your /Python/2.7/site-packages is')

**No DTB connection is needed for the timing experiment, the data is saved to the 'task' folder directly**

**Run the following code:**

Insert subject netID when prompted at the start of all script runs.

    1. Instruction -> run Psychopy_demo.py
    2. Time Perception -> run PsychoPy_Perception.py
    3. Time Production -> run Psychopy_Production.py