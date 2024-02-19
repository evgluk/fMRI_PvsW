# Analysis Pipeline
(0) Behavioral data events is organized as BIDS;

(1) Raw dicom data is converted into [BIDS](http://bids.neuroimaging.io/) format by [dcm2bids](https://github.com/cbedetti/Dcm2Bids) and validated; 

(2) BIDS data quality control is done;

(3) BIDS data preprocessing follows fmriprep pipeline;

(4) Main analysis is going to be updated (as in pre-registration) ...
- GLMs
- RSA
- SVM

## 1. Behavioral data organization
Behavioral data will be collected in two sessions: computer session and fMRI session. 
In this project, behavioral data are recorded as csv files locally on Dell laptops, so after each day's experiment, please run in bash `./move_and_upload_behavioral_data.sh` in 'Scripts' folder to upload all data into DTB. Always be patient and careful while uploading data, if you find anything wrong/weird or need help, please contact Jenya.

After upload all csv data into DTB, please first check whether fMRI id and BIDS id in 'Subject_info.csv' are updated. The fMRI id is subject id used in fMRI experiemnt, and the BIDS id is the one created by `createbids.sh` below. Make sure the subjid, the fMRI id and BIDS id of the current subject are matched. Then run in bash `python3 createbids_beh.py` in 'Scripts' folder to add BIDS events files. 

The output includes 10 columns:
- onset            ---> the onset of the event；
- duration         ---> the duration of the event；
- event_type       ---> event type, Decision, Confirmation, Decision_end (from the onset of decision until the end of that trial) and Confirmation_end (from the onset of confirmation until the end of that trial；
- trial_type       ---> LongDelay_Behavior or ShortDelay_Behavior；
- delayed_reward   ---> rewmag of the delayed option；
- delaytime        ---> delay time of the delayed option；
- choice           ---> decison on current trial, 0--now, 1--delay, n/a--no press；
- outcome_mag      ---> reward magnitude of the chosen option, if no response on current trial, then this is decided by the computer-picked choice, and the same below;
- outcome_delay    ---> delay of the chosen option；
- subjective_value ---> subjective value of the delayed option；

We have 4 events in one trial so that in tsv files, each trial takes 4 lines with each line containing the data of one type. There should be 201 lines in total (200 data lines + 1 head line).
The timing data in the 2nd session in each run are re-computed as follow:
![](img/TD_calculation.PNG)


## 2. Imaging data organization
The imaging data in this project is organized as BIDS. BIDS has its own specification, and can be found [here](https://bids-specification.readthedocs.io/en/latest/03-modality-agnostic-files.html). 
All raw imaging data,  will be stored on fMRI computer: ino ('media/erlichlab/hdd/fMRI_Data_Storage/') and backed up (regularly by Jenya) to choji('/tank/data/fmri/PostponingVsWaiting_fmri'). To organize data as BIDS, please do as follows:
* use samsung external DVD reader to get raw data processed via dicom tool at fMRI Dell laptop and connect external harddrive for output;
* run dicom tool 'Dicom分类1.2.1.exe' on fMRI Dell laptop to convert raw data into dicom data (this .exe file is in Chinese, but straightforward) and save on an external drive. Select the input folder (from DVD reader). When you select the output folder the process starts immediately and takes about 5 minutes per subject. A supporting image from `img/` should appear below;
![](img/DicomTool.jpeg)
* anonymize the created folders by typing subject's fMRI 'initial' IDs instead of names pre-written by fMRI technician;
* then sync to ino by `rsync -av <yourpath> erlichlab@ino:/media/erlichlab/hdd/fMRI_Data_Storage/raw_dicom`; 
* copy the raw data for each new subject to another folder (for processing) by running `sudo rsync -av /media/erlichlab/hdd/fMRI_Data_Storage/raw_dicom/<subID>* /media/erlichlab/hdd/fMRI_Data_Storage/PostponingVSWaiting/sourcedata/`;
* update (comment out old subjids and add new ones) and run the shell script in 'PostponingVSWaiting' folder to create BIDS: `sudo bash createbids.sh`;
* validate the BIDS data with an [online tool](https://bids-standard.github.io/bids-validator/) by running `bids-validator /media/erlichlab/hdd/fMRI_Data_Storage/PostponingVSWaiting/`.

The `createbids.sh` script re-numbers the participants, so that subject with fMRI 'initial' ID sub-007 is now sub-001, in order, consecutively.

IF ERRORS - not OK, also check warnings.

## 3. Imaging data quality check (QC)
Before running pre-processing, several quality checks should be implemented to ensure results are not influenced by artefacts. 
According to pre-registration: "If a BOLD run does not pass this check (checklist is attached), this BOLD run will be removed from further analysis. If more than two runs are excluded for a single subject, we will exclude that subject. If a structural T1-weighted scan does not pass this check, we will also exclude that subject."

QC is done by running MRIQC (quantitative), a package developed by Poldrack's group (the same group as fMRIPrep), and eye-check (qualitative). 

**QC results should be recorded in [Image Data Checklist](https://docs.google.com/spreadsheets/d/1mUHwqQxdk7_U_Nm4U0wOzoJRP9VvBgxaMCfH9mkkecQ/edit?usp=sharing) google sheet (the google sheet)**.

### (1) quantitative check:
- run 'mriqc' with a docker at ino: `sudo docker run -it --rm -v /media/erlichlab/hdd/fMRI_Data_Storage/PostponingVSWaiting:/data:ro -v /media/erlichlab/hdd/fMRI_Data_Storage/PostponingVSWaiting/derivatives/mriqc:/out poldracklab/mriqc:latest /data /out participant -m T1w bold --verbose-reports`; after running MRIQC, both group and individual reports for structural and BOLD data are generated;
- then, run `python3 FD-check.py` in 'Scripts' folder to calculate percentage of over-threshold points and detect outliers; 

Exclusion criteria:

(1) if one's data (both structual and BOLD, the same below) is detected as outlier in any metric (metrics description is [here](https://docs.google.com/spreadsheets/d/1f38P7SK6-N-ajWqtxm91lhVs_N-AVdbmG3hR_CVa0yc/edit#gid=0) and in [official document](https://mriqc.readthedocs.io/en/stable/)); 

(2) main focus should be laid on head motion with FD (Framewise Displacement, see power paper in QC_reference folder), threshold as 0.2 mm, if one is with increasing trend of head motion(check individual report.html generated by MRIQC), or have a point over 2mm (very big value), or his/her FD_num(number of over-threshold data points) is an outlier in group report, or percentage of FD(over 0,2 mm) num is over 20%. 

- finally, record result in **the google sheet**.

### (2) qualitative check:

Access the data to check: 
- locally on ino and by openning 'fsleyes';
- through ssh to ino and X-forwarding by running `ssh erlichlab@ino.shanghai.nyu.edu -Y` and then `fsleyes&`.

Open **the google sheet** and check the imaging data visually according to CBS quality control manual in QC_reference folder. 
This step requires experience of each reviewer, please train your eyes to get familiar with each type of artefacts. Please contact Jenya 
when you finish the check so that she can update fmri.quality_check table in DTB.

**Reviewer!!! Please use your own 'sheet' first, not to be biased by others' results.**
Some useful [online materials](http://chickscope.beckman.uiuc.edu/roosts/carl/artifacts.html).

We pre-registered that "at least two researchers from the project will train their eyes to get familiar with each type of artifacts and follow the guidelines of the control manual".
All check results should be recorded, and it is important to add reasons of excluding one's data!

## 4. Pre-processing (3dDespike + fmriprep)
Before running, **please** check whether data qulity check is done, and the results are updated in DTB. 3dDespike and Preprocessing are ran by using the shell script `./despike_preprocess.sh`. In this script, first, image data are despiked by 3dDespike from the AFNI package, and stored in '/derivatives/despiked_data', then fmriprep finishes the remianing 
steps and saves outputs in '/derivatives/fmriprep'. 

### preprocessing quality check
Quality check after fmriprep is mainly based on the html report files, via visual assessment. Visual reports from fMRIPrep permit: ensuring that the T1w reference
brain was accurately extracted, checking that adequate susceptibility distortion correction was applied, assessing the correctness of the brain mask calculated from the BOLD signal, examining the alignment of BOLD and T1w data, etc.

If you have any question during visual check, please refer to [fmriprep document](https://fmriprep.readthedocs.io/en/latest/outputs.html#) for detailed information of outputs, and [this material](https://andysbrainbook.readthedocs.io/en/latest/OpenScience/OS_Overview.html) provides short instruction
on steps to check the outputs. Further question can be posted on [neurostar](https://neurostars.org/).
- 1. Errors:

Open the html, and click "Error" tag on the top. If no error (this is expected), then move on; if any error is reported, please note it and contact Jenya. Error in preprocessing **SHOULD NOT** be ignored, so we need to figure out the reason and re-preprocess these data. Jenya noticed some errors in preprocessing in parallel, seems like not everything is finished, when the script finishes...

- 2. visual assessment of structural figures

2.1 The first image you should see is Brain mask and brain tissue segmentation of the T1w, where the red line encompasses the entire brain, the blue line encompasses white matter, and magenta encompasses the cerebral spinal fluid (CSF). **Attention**: the colormap has changed since last time Shengjie reported to "the estimated brain mask is outlined in red, the grey matter boundary is outlined in magenta, and the white matter boundary is outlined in blue" according to these [guidelines](https://andysbrainbook.readthedocs.io/en/latest/OpenScience/OS/fMRIPrep_Demo_3_ExaminingPreprocData.html). This will give you an idea of the quality of the skull extraction. Basically, reviewers need to check whether the contours outline the brain structure well, such as no suspicious gap between the contour and the brain, no cross or break of the contour and no mismatched contour on the brain structure etc...

2.2 The second image you should see is Spatial normalization of the anatomical T1w reference; if you hover your mouse over the image, it will display the back and forth between the anatomical and standard template. This allows you to assess the quality of the normalization step. Here, reviewers need to check the the size are identical, any gap, signal loss, mismatched areas or other weird issues exist.

- 3. visual assessment of functional figures:

In functional images check, please note, images in some sections are not the final outputs since they are extracted at that step to be displayed as visual evidence of relevant pre-processing step. And EPI is more blurred than structural images, so the shape and size might be unclear somewhere. Unless some areas have serious quality issues or they are fine at most time. 

3.1 SDC-SYN estimates warping, and then tries to reinstate the original brain structure. The main focus of the SDC-SyN panels is the accuracy of that estimation. Simply, hover the mouse over the image to see the before SDC and after SDC.If the blue contour aligns better with data after SDC-SyN, then we should use the correction, and this is also a proof that it works well. The blue contour still outlines white matter.

3.2 Alignment of functional and anatomical MRI data
This shows the quality of the co-registration step. Fixed is structural image and the moving is mean functional image. The reviewer need to check whether two images are matched, so do contours.

3.3 Brain mask and (temporal/anatomical) CompCor ROIs
This shows the brain tissue ROIs used to generate the CompCor confounds.The visual assessment is to check whether the whole brain is outlined well by the red contour.

3.4 BOLD summary
This provides information regarding the level of motion present in the run. Four lines indicate global signals in each structure. Do not compare lines across run, session or subject as their reference lines are different. The reference line is close to its mean value. If huge spike was found, then this run is bad. But we have done this in MRIQC, so here we are re-checking to see if despike removes big spikes and whether the siganl quality improves after preprocessing in pass-MRIQC-criterion data. A carpet plot shows the time series for all voxels within the brain mask. Voxels are grouped into cortical (blue), and subcortical (orange) gray matter, cerebellum (green) and white matter and CSF (red), indicated by the color map on the left-hand side. As a rule of thumb, any dark lines, whits lines or specific pattern is not good. If it looks random to you, then it is usually okay.

- Hint: to check contours, one can pay attention to ventricles, cortexes and cerebellum as landmarks as they are big and clear to check.
- [Examples of accepted images](img/sub-002.html). Gitlab cannot render the html file so that the reviewer need to open the example file with browser instead.
- The example is from sub-002, whose run1 is a good example to serve as reference of each visual assessment.


## 5. Univariate Analyses of Imaging Data
All statistical analyses are running with FSL. Data which do not pass quality check are not included in following analyses.
### Generating EV files.
EV files are required for building GLMs in FSL. In our project, we have two types of EV files: confounds and timing. The former consists of 6 motion parameters and FD. The timing EV files are based on each GLM design, so there would be four groups of EV files. 
To get the EV, please comment out un wanted ones at the end to generate needed EV files, and then run `python3 createEV.py` in terminal or use your desired python interpreter. All EV files will be saved in `/PostponingVSWaiting/derivatives/EV` in confounds or 
contrast folder respectively. Timing EV files are using 3-column format, in GLM1, the third column consists of 1s as default, while in GLM2-4, the third column contains reward (if confirmation epoch - actual mag/delay) mag/delay/SV (logk) as described in the preregister, and they are all raw values.

For parametric models GLM2-4 also considering additional model with 1s + de-meaned values per run (intercept + slope), but there are several concerns about this in literature, including that the means are different across several runs our subjects have (the same critique is also applied to z-scores per run).


### 1st level analysis
The fsf files contain GLM design information and can be used for batch processing of 1st level analysis. The codes to prepare and run fsf files are put in `/PostponingVSWaiting/code`, and named as GLM1-3_1st.sh (did GLM1_1d_1st.sh for testing purposes; GLM1_1d is the correct first model now, since decision epoch only goes till the end of decision) and GLM4_1st.sh. The former is used to run GLM1 to GLM3 in order, 
and the later is used for GLM4. The outputs are saved in `/PostponingVSWaiting/derivativesanalysis/GLMx`. In each GLM folder, 1st_level folder contains model building information, including template fsf file (it is a template as it does not have specific input of one run, but 
its settings is used in building current GLM) and fsf files for each run (saved as subjID_GLM_run_design.fsf). Please note, the template fsf files are different between GLM1-3 and GLM4. The shell script includes the check function for already finished runs, so to run new analesis,
just change directory to `~/PostponingVSWaiting/code` and run `./GLM1-3_1st.sh` (`./GLM1_1d_1st.sh` see above) or `./GLM4_1st.sh`. The script also calls a python file called filter.py, this is used to visit recordings in dtb and then remove runs which fail passing quality-check from analysis.

QC as Mumford suggests, registration is done in fMRI prep - so do not look at the registration images, although they exist.

Check matrix and collinearity (because of collinearity issue we changed decision_end to decision epoch). The \% effect required is suggested to be less than 2. Only diagonal should be white on the matrix.

`grep 'error' sub*/run*.feat/report_log.html`

`ls sub*/run*.feat/stats/zstat1.nii.gz`

The above lines of code will check whether there are errors and whether z-stats are present (you can count the number of files).

#### 5.1 GLM1-3
5.1.1 The main aim of GLM1 is to locate brain region corresponding to temporal context (waiting vs postponing). 

- Decision: from onset of decision until the confirmation
- Confirmation: from onset of confirmation until the onset of new trial

5.1.2 The main aim of GLM2 is to investigate positive parametric modulation of the valuation network with reward magnitude of delayed option.

- Decision: from onset of decision until the confirmation
- Confirmation: from onset of confirmation until the onset of new trial
- delayed reward magnitute for decision and chosen reward mafnitute for confirmation as parametric modulators

5.1.3 The main aim of GLM3 is to investigate negative parametric modulation of the valuation network with delay duration during the choice epoch)

- Decision: from onset of decision until the confirmation
- Confirmation: from onset of confirmation until the onset of new trial
- delay values as parametric modulators for decision and chosen delay for confirmation

#### 5.2 GLM4
The main goal of GLM4 is to investigate in which regions BOLD signal predicts the SV on each trial and whether these regions differed in long and short conditions

- Decision: from onset of decision until the offset of decision
- SV as parametric modulators

### 2nd level analysis
2nd level analysis is at subject level, i.e., combine results from each run into results for each subject. On the 2nd level we use Fixed Effects.

*BEFORE RUNNING 2nd LEVEL* to avoid fsl registration problem, please change 
directory to `~/PostponingVSWaiting/code` and then run `bash ./replace_regfile.sh` to remove existing registration folders (if any) and .mat files; and move/replace mat/nii.gz file as suggested by [Mumford](https://mumfordbrainstats.tumblr.com/post/166054797696/feat-registration-workaround).

After this, please run `GLM1-3_2nd.sh` for GLM1 to GLM3 and `GLM4_2nd.sh` for GLM4 to apply 2nd level analysis. Here, some subjects only have 3 or 2 valid runs, the codes
will automatically count the run number and select correct template fsf. If error jumps out, please check whether the run number is correct for current subject.
2nd level analysis results are saved as sub-xxx.gfeat in each subject's folder.

According to mumford's blog, we need to check some files to ensure whether the replacement and 2nd level analysis go well. I could check this manually by checking errors in log: 

`grep 'error' sub*/*.gfeat/report_log.html`

Check transformation to standard space - yellow nice brain
and missing-mask voxels - color only outside. For displaying statistics Mumford likes to use bg_image.nii.gz in fsleyes.

Also, check registration through voxel intensity check: `python3 intensity_check.py`. If check_result.csv contains any not 'Passed' columns, double check.

### 3rd level analysis
3rd level analysis is at the group level, i.e., combine lower-level FEAT directories from each subject into group result. On the 3rd level we use Mixed Effects to generalize our results to the population our sample was drawn from.

For the lower-level FEAT directories we use cope images for each contrast, so analysis will run separately per contrast, averaging the group results. Please pay attention that even under contrast 8  - cope8.feat/stats/ we only have cope1.nii.gz file. 

Please run `GLM1-3_3rd.sh` for GLM1 to GLM3 and `GLM4_3rd.sh` for GLM4 to apply 3rd level analysis.

QC: look at log for errors, significant clusters. The file mask.nii.gz is the one [Mumford suggests](https://www.youtube.com/watch?v=49WGLPZNTrQ&list=PLB2iAtgpI4YHlH4sno3i3CUjCofI38a-3&index=17) to look at using fsleyes, add bg.image.nii.gz (background image, everyone's registration together - resolution in anatomy you have, not standard MNI image). Open thresh.zstat1.nii.gz (corrected for multiple comparison) - red/yellow. Also can check the filtered_func_data.nii.gz image (anything weird too bright or too dark might be an issue).

In order to run a two-sample test (between those whose discount factors in seconds and in days are close AND those for whom these are more apart) for the GLM1, as listed in the preregistered analysis - use `GLM1_3rd2.sh`

In order to run a 3rd-level analysis for GLM4 with additional covariate (similarity in discount factors) - use `GLM_pd_3rdcov.sh`

### Post-hoc analysis

Decided to setup additional parametric models with '_pd' - decision epoch. Decided against additional parametric models for confirmation epoch. The main reason is the same average mag and delay across runs, but not actual reward magnitude and actual time to wait till reward. 

First issue is that in order to make the parametric modulatorsorthogonal to the regressors they are modulating (this reduces the correlation with the main regressor) you should mean-center them. Then, it seems reasonable to model the mean activation and the departure from the mean activation with separate EVs. That would mean having one EV where the third column is all 1's and a second EV where you have the demeaned values. This models the BOLD change as a linear effect around a non-zero mean.

So, Jenya went ahead and created 4 EVs with 4 contrasts for three parametric models (GLM2_pd, GLM3_pd, GLM4_pd).

1. Short: decision till confirmation, with third column - ones;
2. Short: decision till confirmation, with third column - demeaned value;
3. Long: decision till confirmation, with third column - ones;
4. Long: decision till confirmation, with third column - demeaned value.

Contrasts:

1. pds [0 1 0 0]
2. pdl [0 0 0 1]
3. pds>pdl [0 1 0 -1]
4. pdl>pds [0 -1 0 1]

To run all levels use:
`GLM2-4_pd_1st.sh`; `GLM_pd_2nd.sh`; `GLM_pd_3rd.sh`; `GLM_pd_3rdcov.sh`.

Decided to setup yet additional parametric models with '_pdu'. 'u' stand for united nonparametric regressor 'Delay', in every other way the models are similar to the '_pd' ones. Matrices on the first-level after QA check were better for '_pdu' models (compared to '_pd' models). So, Jenya went ahead and created 3 EVs with 4 contrasts for three parametric models (GLM2_pdu, GLM3_pdu, GLM4_pdu).

1. Delay (Short and Long trials combined): decision till confirmation, with third column - ones;
2. Short: decision till confirmation, with third column - demeaned value;
3. Long: decision till confirmation, with third column - demeaned value.

Contrasts:

1. pds [0 1 0]
2. pdl [0 0 1]
3. pds>pdl [0 1 -1]
4. pdl>pds [0 -1 1]

To run all levels use:
`GLM2-4_pdu_1st.sh`; `GLM_pd_2nd.sh`; `GLM_pd_3rd.sh`; `GLM_pd_3rdcov.sh`.

Since scholarship is diverse whether to run parametric analysis for 'delay' or 'inverse delay', Jenya went ahead and created the following GLM3 models: '_pdn(u)' and '_pdinv(u)' - where in the first case only first two contrasts are changed:

1. pds [0 -1 0]
2. pdl [0 0 -1]

and for the inverse delay models instead of mean-centered delay, mean-centered inverse delay is used (to be exact 30/x vs 1/x was used for transformation, where x is delay).

To run all levels use:
`GLM3_pdn(u)_1st.sh` or `GLM3_pdinv(u)_1st.sh`; `GLM_pd_2nd.sh`; `GLM_pd_3rd.sh`; `GLM_pd_3rdcov.sh`.

Finally, Jenya also decided to skull strip functional images using fslmaths function:
`fslmaths func -mul func_brain_mask func_brain`

Then, Jenya re-ran all the following models with the resulted brain functional image: GLM1_1db, GLM2_pdub, GLM3_pdub, GLM4_pdub, GLM3_pdinvub.

To run 1st level use:
`GLM1_1db_1st.sh`,`GLM2-4_pdub_1st.sh` or `GLM3_pdinvub_1st.sh`; the usual ones for the later analysis.

## 6. Multivariate Analysis of Imaging Data
As preregistered, we are going to apply RSA on our imaging data as multivariate analysis, and the [RSA toolbox](https://www.mrc-cbu.cam.ac.uk/methods-and-resources/toolboxes/) will be used. The location of this toolbox is `/media/erlichlab/hdd/tools/rsatoolbox-develop`. Especially, we will follow and modify the [code](https://github.com/zhihao13/Zhang_et_al_17) from Zhang et al. (2017) in our own analysis. 

### 6.1 Extract betamaps.
RSA toolbox only uses betamaps from data processed by SPM in default, and Zhang's code uses data from brainvoyager, however in our case, we process data via FSL. Consenquently, we need to extract betamaps first to build up RDMs (aka representational dissimilarity matrix), and RDM is basic data unit used in RSA. 

To do so, one can run `fslmeants -i peX.nii.gz -o allbetas_peX.txt --showall` for each cope (see description below if you are not familiar with pe). Please navigate to the location of target pe files to extract betamaps, and set output dir for your txt files. You can check the pregistration and FSL design file of each run to see which PEe are needed. A bash script is strongly recommanded for this work. I did not write one because the output txt file of one cope is large (> 4MB), so please decide by yourself whether you would like to extract betamaps in matlab (see [this](https://neuroimager.wordpress.com/2012/10/26/running-fsl-commands-from-matlab/) to learn how to run FSL in matlab) during analysis instead of storing the betamaps txts or, you would like to save these txts first and then run analysis.

The content of each txt file consists of four rows and > 100,000 columns. The first three rows store x,y,z coordinates, and the bottom row stores beta values. Please check whether the size of x,y,z is consistant across all copes of all subjects. 

#### Descripition of PE
After 1st_level, FSL generates cope, pe, varcope, zstat tstat, and so on in stats file. The cope stands for contrast of parameter estimate, which represents eight contrasts of beta values. PEs (parameter estimate) are the beta estimates from the GLM, the first eight PEs are estimate of eight EVs we set in design.fsf (not contrasts), and the last seven PEs are motion parameters plus Framewise Displacement. Varcope is variance (Error) image for each contrast, zstat/tstat is (unthresholded) T and Z statistics for each of our contrasts. 

### 6.2 Build up RDM
...

## Others
### Simulation
This folder contains all scripts for simulation work. The purpose of simulation is to find an optimal choice set for computer session, which can cover different ks as broadly as possible.

(1) figure folder consists of R2 graphs of top 5 sets in simulation_3;

(2) maincode folder has all codes for running simulation;

(3) output folder includes simulation output in 3 simulations, sorted data are key part of each output that saved into DTB.

The difference between 3 simulation runs is they have different ratio of delay time, the first one uniformly picked delay time from[1, 64] with average delay time being ~32s; delay time ratio in the second one is 90% (1-30) and 10% (30-64), average is ~24; delay time ratio in the third one is 70% (1-15), 20% (15-30) and 10% (30-64), average is ~15s.

### Smoothing issues in MVPA
I did some reading on whether smoothing should be removed in MVPA analysis. This topic is highly [debated](https://www.hindawi.com/journals/cmmm/2012/961257/). Some suggest it depends on [analysis strategy](https://groups.google.com/forum/#!topic/mvpa-toolbox/DMY0OJlp9Iw). However, major viewpoint is we don't apply smoothing or apply minimum one to [preserve fine-grained subject-specific information](https://www.sciencedirect.com/science/article/pii/S1053811909006727?via%3Dihub), although [one paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5446978/) tested different levels of smoothing with motion task in correlation-based MVPA and found smoothing has limited influence in their case. 
Futhermore, smoothing is not included in fMRIPrep, and it outcomes still has good performance compared to those from FEAT pipeline in FSL which has smoothing. And I also found [one decision-making study](http://psych.wisc.edu/postlab/readings/jimura_poldrack_2012.pdf) who did not apply smoothing. So my thought is, if we use fMRIPrep to preprocess our data, then we are fine with smoothing issues, and are safe to do subsequent MVPA analysis. 

### backup
In analysis folder, I create a backup folder to store old analysis outputs. Currently, the GLM3 with all stimilus delay (non-zero) as modulator is stored there, named GLM3_nozero.
