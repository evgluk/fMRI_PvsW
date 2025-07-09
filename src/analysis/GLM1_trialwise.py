#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# codes of GLM1, decoding
# =============================================================================
import os
import glob
import pandas as pd
import numpy as np
from nilearn.image import load_img
from nilearn.plotting import plot_design_matrix
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm.thresholding import threshold_stats_img
from nilearn.image import math_img
from nilearn.reporting import make_glm_report
from nilearn.reporting import get_clusters_table

# get Run IDs
def read_runID(subID):
    runID = []
    files = glob.glob('behavior_data/EV_contrast/GLM1/{}_LongDelay_*_decision.tsv'.format(subID)) # specify your path accordingly
    for f in files:
        runID.append(int(f[-14]))
    runID.sort()
    
    print('there are {} runs in this subject {}'.format(len(runID), subID))
    
    return runID

# add trial ids into trial_type
def lss_transformer(events_df, runID, nrow):
    events = events_df.copy()

    # Determine which number trial it is *within the condition*
    trial_condition = events.loc[nrow, "trial_type"]
    trial_type_series = events["trial_type"]
    trial_type_series = trial_type_series.loc[
        trial_type_series == trial_condition
    ]

    trial_type = events['trial_type'].unique()[0]
    trial_name = "{}_run{}_trial{}".format(trial_type, runID, nrow+1)
    events.loc[nrow, "trial_type"] = trial_name
    
    return events

# prepare event files
def event_maker(subID, runID, nrow):
    colnames = ['onset', 'duration', 'intercept']
    decision_long = pd.read_csv('behavior_data/EV_contrast/GLM1/{}_LongDelay_fMRI_run-0{}_decision.tsv'.format(subID, runID), 
                                sep='\t', header = None, names = colnames, index_col=False) # specify your path accordingly
    confirmation_long = pd.read_csv('behavior_data/EV_contrast/GLM1/{}_LongDelay_fMRI_run-0{}_confirmation_end.tsv'.format(subID, runID), 
                                sep='\t', header = None, names = colnames, index_col=False) # specify your path accordingly
    decision_short = pd.read_csv('behavior_data/EV_contrast/GLM1/{}_ShortDelay_fMRI_run-0{}_decision.tsv'.format(subID, runID), 
                                sep='\t', header = None, names = colnames, index_col=False) # specify your path accordingly
    confirmation_short = pd.read_csv('behavior_data/EV_contrast/GLM1/{}_ShortDelay_fMRI_run-0{}_confirmation_end.tsv'.format(subID, runID), 
                                sep='\t', header = None, names = colnames, index_col=False) # specify your path accordingly
    
    decision_long['trial_type'] = 'decision_long'
    confirmation_long['trial_type'] = 'confirmation_long'
    decision_short['trial_type'] = 'decision_short'
    confirmation_short['trial_type'] = 'confirmation_short'
    
    decision_long = lss_transformer(decision_long, runID, nrow)
    confirmation_long = lss_transformer(confirmation_long, runID, nrow)
    decision_short = lss_transformer(decision_short, runID, nrow)
    confirmation_short = lss_transformer(confirmation_short, runID, nrow)
    
    events = pd.concat([decision_long, confirmation_long, decision_short, confirmation_short], ignore_index=True)
        
    return events

# prepare confounds files
def confounds_maker(subID, r):
    final_colnames = []
    
    confounds = pd.read_csv('imgdata/{}/func/{}_task-delay_run-0{}_desc-confounds_timeseries.tsv'.format(subID, subID, r),
                             sep = '\t') # specify your path accordingly
    confoundscol = ['csf','white_matter', 'framewise_displacement', 'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'] + [i for i in list(confounds) if 'cosine' in i]
    confounds = confounds[confoundscol]
    confounds = confounds.fillna(0)
    
    colnames = list(confounds)
    if len(final_colnames) < len(colnames):
        final_colnames = colnames
  
    return confounds

# define all contrasts
def contrasts_maker(design_matrix,runID, nrow):
    contrast_matrix = np.eye(design_matrix.shape[1])
    contrasts = {
        column: contrast_matrix[i]
        for i, column in enumerate(design_matrix.columns)
    }

    contrasts["decision_short_run{}_trial{} - decision_long_run{}_trial{}".format(runID, nrow+1,runID, nrow+1)] = (
        contrasts["decision_short_run{}_trial{}".format(runID, nrow+1)] - contrasts["decision_long_run{}_trial{}".format(runID, nrow+1)]
    )
    
    contrasts["decision_long_run{}_trial{} - decision_short_run{}_trial{}".format(runID, nrow+1,runID, nrow+1)] = (
        contrasts["decision_long_run{}_trial{}".format(runID, nrow+1)] - contrasts["decision_short_run{}_trial{}".format(runID, nrow+1)]
    )
    
    contrasts["confirmation_short_run{}_trial{} - confirmation_long_run{}_trial{}".format(runID, nrow+1,runID, nrow+1)] = (
        contrasts["confirmation_short_run{}_trial{}".format(runID, nrow+1)] - contrasts["confirmation_long_run{}_trial{}".format(runID, nrow+1)]
    )
    
    contrasts["confirmation_long_run{}_trial{} - confirmation_short_run{}_trial{}".format(runID, nrow+1,runID, nrow+1)] = (
        contrasts["confirmation_long_run{}_trial{}".format(runID, nrow+1)] - contrasts["confirmation_short_run{}_trial{}".format(runID, nrow+1)]
    )
   
    return contrasts

# individual-level analysis, loop over subjects
def first_level_glm(sublist, smooth):
    for subID in sublist:
        
        print('model fitting on {} is starting'.format(subID))
        
        # saving model outputs
        if not os.path.exists('GLM1_results_decoding'):
            os.mkdir('GLM1_results_decoding')
        directory = 'GLM1_results_decoding/{}'.format(subID)
        if not os.path.exists(directory):
            os.mkdir(directory)
        
        runIDs = read_runID(subID)
    
        for runID in runIDs:
            func = load_img('imgdata/{}/func/{}_task-delay_run-0{}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'.format(subID, subID, runID)) # specify your path accordingly
            # sub_imgs.append(func)
            for nrow in range(25):
             
                events = event_maker(subID, runID, nrow)
                confounds = confounds_maker(subID, runID)
                
                fmri_glm = FirstLevelModel(t_r = 1.74,
                                           noise_model = 'ar1',
                                           hrf_model = 'spm',
                                           drift_model = None, # I already have cosine values in confounds files
                                           signal_scaling = False,
                                           minimize_memory = False,
                                           smoothing_fwhm = smooth)
                
                fmri_glm = fmri_glm.fit(func, events, confounds)
                matrix = fmri_glm.design_matrices_[0]
            
                # matrix = matrix_maker(matrix_list)
                contrasts = contrasts_maker(matrix,runID, nrow)
                
                # I only save a matrix for the first trial in each run as an example
                if nrow == 0:
                    matrix.to_csv('GLM1_results_decoding/{}/design_matrix_run{}_trial{}.csv'.format(subID, runID, nrow+1), sep=',', index=False)
                    plot_design_matrix(matrix, output_file = 'GLM1_results_decoding/{}/design_matrix_run{}_trial{}.png'.format(subID, runID, nrow+1))
            
                decision_long_output = fmri_glm.compute_contrast(
                    contrasts["decision_long_run{}_trial{}".format(runID, nrow+1)],
                    output_type="all",
                )
                
                decision_short_output = fmri_glm.compute_contrast(
                    contrasts["decision_short_run{}_trial{}".format(runID, nrow+1)],
                    output_type="all",
                )
                
                confirmation_long_output = fmri_glm.compute_contrast(
                    contrasts["confirmation_long_run{}_trial{}".format(runID, nrow+1)],
                    output_type="all",
                )
                
                confirmation_short_output = fmri_glm.compute_contrast(
                    contrasts["confirmation_short_run{}_trial{}".format(runID, nrow+1)],
                    output_type="all",
                )
                
                # long > short
                decision_long_short_output = fmri_glm.compute_contrast(
                    contrasts["decision_long_run{}_trial{} - decision_short_run{}_trial{}".format(runID, nrow+1,runID, nrow+1)],
                    output_type="all",
                )
                
                # short > long
                decision_short_long_output = fmri_glm.compute_contrast(
                    contrasts["decision_short_run{}_trial{} - decision_long_run{}_trial{}".format(runID, nrow+1,runID, nrow+1)],
                    output_type="all",
                )
                
                confirmation_long_short_output = fmri_glm.compute_contrast(
                    contrasts["confirmation_long_run{}_trial{} - confirmation_short_run{}_trial{}".format(runID, nrow+1,runID, nrow+1)],
                    output_type="all",
                )
                
                confirmation_short_long_output = fmri_glm.compute_contrast(
                    contrasts["confirmation_short_run{}_trial{} - confirmation_long_run{}_trial{}".format(runID, nrow+1,runID, nrow+1)],
                    output_type="all",
                )
                
                # saving model outputs
                if not os.path.exists('GLM1_results_decoding'):
                    os.mkdir('GLM1_results_decoding')
                directory = 'GLM1_results_decoding/{}'.format(subID)
                if not os.path.exists(directory):
                    os.mkdir(directory)
                
                if smooth == False:
                    smooth_index = 'unsmoothed'
                else:
                    smooth_index = 'smoothed'
                
                # save contrasts
                np.save('GLM1_results_decoding/{}/decision_long_{}.npy'.format(subID, smooth_index), decision_long_output)
                np.save('GLM1_results_decoding/{}/decision_short_{}.npy'.format(subID, smooth_index), decision_short_output)
                np.save('GLM1_results_decoding/{}/confirmation_long_{}.npy'.format(subID, smooth_index), confirmation_long_output)
                np.save('GLM1_results_decoding/{}/confirmation_short_{}.npy'.format(subID, smooth_index), confirmation_short_output)
                
                # beta values
                decision_long_output['effect_size'].to_filename('GLM1_results_decoding/{}/decision_long_beta_{}_run{}_trial{}.nii.gz'.format(subID, smooth_index, runID, nrow+1))
                decision_short_output['effect_size'].to_filename('GLM1_results_decoding/{}/decision_short_beta_{}_run{}_trial{}.nii.gz'.format(subID, smooth_index, runID, nrow+1)) 
                confirmation_long_output['effect_size'].to_filename('GLM1_results_decoding/{}/confirmation_long_beta_{}_run{}_trial{}.nii.gz'.format(subID, smooth_index, runID, nrow+1)) 
                confirmation_short_output['effect_size'].to_filename('GLM1_results_decoding/{}/confirmation_short_beta_{}_run{}_trial{}.nii.gz'.format(subID, smooth_index, runID, nrow+1)) 
                decision_long_short_output['effect_size'].to_filename('GLM1_results_decoding/{}/decision_long_short_beta_{}_run{}_trial{}.nii.gz'.format(subID, smooth_index, runID, nrow+1))
                decision_short_long_output['effect_size'].to_filename('GLM1_results_decoding/{}/decision_short_long_beta_{}_run{}_trial{}.nii.gz'.format(subID, smooth_index, runID, nrow+1)) 
                confirmation_long_short_output['effect_size'].to_filename('GLM1_results_decoding/{}/confirmation_long_short_beta_{}_run{}_trial{}.nii.gz'.format(subID, smooth_index, runID, nrow+1)) 
                confirmation_short_long_output['effect_size'].to_filename('GLM1_results_decoding/{}/confirmation_short_long_beta_{}_run{}_trial{}.nii.gz'.format(subID, smooth_index, runID, nrow+1)) 
                

    
if __name__ == '__main__':
    sublist = os.listdir('imgdata/') # specify the path where all preprocessed data are stored
    sublist.remove('.DS_Store') # for mac users to get rid of DS_store from the subject list
    sublist.sort()
    
    # fit first-level models, unsmoothed
    first_level_glm(sublist, smooth = False)
    

