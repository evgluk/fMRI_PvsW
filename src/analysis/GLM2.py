#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# codes of GLM2, parametric modulation of reward magnitude
# =============================================================================
import os
import glob
import pandas as pd
import numpy as np
from nilearn.image import load_img
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.plotting import plot_design_matrix
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm.thresholding import threshold_stats_img
from nilearn.reporting import make_glm_report
from nilearn.reporting import get_clusters_table

# get Run IDs
def read_runID(subID):
    runID = []
    files = glob.glob('behavior_data/EV_contrast/GLM2/{}_LongDelay_*_decision_dm.tsv'.format(subID))
    for f in files:
        runID.append(int(f[-17]))
    runID.sort()
    
    print('there are {} runs in this subject {}'.format(len(runID), subID))
    
    return runID

# make design matrix, slelect the one with minimum regressors for following contrasts
def matrix_maker(matrix_list):
    nmatrix = len(matrix_list)
    if nmatrix == 4:
        matirx1_ncol = matrix_list[0].shape[1]
        matirx2_ncol = matrix_list[1].shape[1]
        matirx3_ncol = matrix_list[2].shape[1]
        matirx4_ncol = matrix_list[3].shape[1]
        
        min_ncol = min([matirx1_ncol, matirx2_ncol, matirx3_ncol, matirx4_ncol])
        
        if matirx1_ncol == min_ncol:
            matrix = matrix_list[0]
        elif matirx2_ncol == min_ncol:
            matrix = matrix_list[1]
        elif matirx3_ncol == min_ncol:
            matrix = matrix_list[2]
        elif matirx4_ncol == min_ncol:
            matrix = matrix_list[3]
    
    if nmatrix == 3:
        matirx1_ncol = matrix_list[0].shape[1]
        matirx2_ncol = matrix_list[1].shape[1]
        matirx3_ncol = matrix_list[2].shape[1]

        min_ncol = min([matirx1_ncol, matirx2_ncol, matirx3_ncol])
        
        if matirx1_ncol == min_ncol:
            matrix = matrix_list[0]
        elif matirx2_ncol == min_ncol:
            matrix = matrix_list[1]
        elif matirx3_ncol == min_ncol:
            matrix = matrix_list[2]
    
    if nmatrix == 2:
        matirx1_ncol = matrix_list[0].shape[1]
        matirx2_ncol = matrix_list[1].shape[1]

        min_ncol = min([matirx1_ncol, matirx2_ncol])
        
        if matirx1_ncol == min_ncol:
            matrix = matrix_list[0]
        elif matirx2_ncol == min_ncol:
            matrix = matrix_list[1] 
            
    return matrix

# make design matrix for parametric modulation
def matrix_designer_dm(subID):
    runID = read_runID(subID)
    matrix_list = []
    final_confounds_colnames = []
    tr = 1.74
    
    for r in runID:
        # read func data for number of scans
        func = load_img('imgdata/{}/func/{}_task-delay_run-0{}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'.format(subID, subID, r)) # specify your path accordingly
        nscans = np.shape(func)[-1]
        frame_times = np.arange(nscans) * tr
        
        # read task info
        colnames = ['onset', 'duration', 'modulation']
        decision_long = pd.read_csv('behavior_data/EV_contrast/GLM2/{}_LongDelay_fMRI_run-0{}_decision_dm.tsv'.format(subID, r), 
                                    sep='\t', header = None, names = colnames, index_col=False)
        decision_short = pd.read_csv('behavior_data/EV_contrast/GLM2/{}_ShortDelay_fMRI_run-0{}_decision_dm.tsv'.format(subID, r), 
                                    sep='\t', header = None, names = colnames, index_col=False)
        
        decision_long['trial_type'] = 'decision_long_pm'
        decision_short['trial_type'] = 'decision_short_pm'

        events_pm = pd.concat([decision_long, decision_short], ignore_index=True)
        # events_pm['modulation'] = events_pm['modulation'] - events_pm['modulation'].mean() # values from modulation is de-meaned
        
        # read confounds info
        confounds = pd.read_csv('imgdata/{}/func/{}_task-delay_run-0{}_desc-confounds_timeseries.tsv'.format(subID, subID, r),
                                  sep = '\t') # specify your path accordingly
        confoundscol = ['csf','white_matter', 'framewise_displacement', 'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'] + [i for i in list(confounds) if 'cosine' in i]
        confounds = confounds[confoundscol]
        confounds = confounds.fillna(0)
        
        confounds_colnames = list(confounds)
        if len(final_confounds_colnames) < len(confounds_colnames):
            final_confounds_colnames = confounds_colnames
        
        # make regular matrix with modulation
        dm_pm = make_first_level_design_matrix(frame_times, events_pm,
                                               drift_model = None,
                                               add_regs = confounds,
                                               add_reg_names = confounds_colnames)
        
        # make regular matrix without modulation
        decision_long['trial_type'] = 'decision_long'
        decision_short['trial_type'] = 'decision_short'
        events_pm = pd.concat([decision_long, decision_short], ignore_index=True)
        events = events_pm[['onset', 'duration','trial_type']]
        
        dm = make_first_level_design_matrix(frame_times, events,
                                            drift_model = None)
        
        # finilize the matrix
        matrix_pm = pd.concat([dm.iloc[:,0:2], dm_pm], axis=1)
        matrix_pm.to_csv('GLM2_results/{}/design_matrix_run-0{}.csv'.format(subID, r), sep=',', index=False)
        plot_design_matrix(matrix_pm, output_file = 'GLM2_results/{}/design_matrix_run-0{}.png'.format(subID, r))
        
        matrix_list.append(matrix_pm)
        
    return matrix_list

# define all contrasts
def contrasts_maker(design_matrix):
    contrast_matrix = np.eye(design_matrix.shape[1])
    contrasts = {
        column: contrast_matrix[i]
        for i, column in enumerate(design_matrix.columns)
    }

    contrasts["decision_short_pm - decision_long_pm"] = (
        contrasts["decision_short_pm"] - contrasts["decision_long_pm"]
    )
    
    contrasts["decision_long_pm - decision_short_pm"] = (
        contrasts["decision_long_pm"] - contrasts["decision_short_pm"]
    )
   
    return contrasts
    
# individual-level analysis, loop over subjects
def first_level_glm(sublist, smooth):
    for subID in sublist:
        
        print('model fitting on {} is starting'.format(subID))
        
        # saving model outputs
        if not os.path.exists('GLM2_results'):
            os.mkdir('GLM2_results')
        directory = 'GLM2_results/{}'.format(subID)
        if not os.path.exists(directory):
            os.mkdir(directory)
        
        sub_imgs = []
        runID = read_runID(subID)
    
        for r in runID:
            func = load_img('imgdata/{}/func/{}_task-delay_run-0{}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'.format(subID, subID, r)) # specify your path accordingly
            sub_imgs.append(func)
        
        fmri_glm = FirstLevelModel(t_r = 1.74,
                                    noise_model = 'ar1',
                                    hrf_model = 'spm',
                                    drift_model = None, # I already have cosine values in confounds files
                                    signal_scaling = False,
                                    minimize_memory = False,
                                    smoothing_fwhm = smooth) 

        matrix_list = matrix_designer_dm(subID)
        
        fmri_glm = fmri_glm.fit(sub_imgs, design_matrices = matrix_list)
        
        # shape all matrices into the same shape
        matrix_contrast = matrix_maker(matrix_list)
        contrasts = contrasts_maker(matrix_contrast)
    
        decision_long_output = fmri_glm.compute_contrast(
            contrasts['decision_long_pm'],
            output_type="all",
        )
        
        decision_short_output = fmri_glm.compute_contrast(
            contrasts['decision_short_pm'],
            output_type="all",
        )
        
        # long > short
        decision_long_short_output = fmri_glm.compute_contrast(
            contrasts['decision_long_pm - decision_short_pm'],
            output_type="all",
        )
        
        # short > long
        decision_short_long_output = fmri_glm.compute_contrast(
            contrasts['decision_short_pm - decision_long_pm'],
            output_type="all",
        )
        
        if smooth == False:
            smooth_index = 'unsmoothed'
        else:
            smooth_index = 'smoothed'
            
        # beta values
        decision_long_output['effect_size'].to_filename('GLM2_results/{}/decision_long_pm_beta_{}.nii.gz'.format(subID, smooth_index))
        decision_short_output['effect_size'].to_filename('GLM2_results/{}/decision_short_pm_beta_{}.nii.gz'.format(subID, smooth_index)) 
        decision_long_short_output['effect_size'].to_filename('GLM2_results/{}/decision_long_short_pm_beta_{}.nii.gz'.format(subID, smooth_index))
        decision_short_long_output['effect_size'].to_filename('GLM2_results/{}/decision_short_long_pm_beta_{}.nii.gz'.format(subID, smooth_index)) 
        
        # z values
        decision_long_output['z_score'].to_filename('GLM2_results/{}/decision_long_pm_zstat_{}.nii.gz'.format(subID, smooth_index))
        decision_short_output['z_score'].to_filename('GLM2_results/{}/decision_short_pm_zstat_{}.nii.gz'.format(subID, smooth_index)) 
        decision_long_short_output['z_score'].to_filename('GLM2_results/{}/decision_long_short_pm_zstat_{}.nii.gz'.format(subID, smooth_index))
        decision_short_long_output['z_score'].to_filename('GLM2_results/{}/decision_short_long_pm_zstat_{}.nii.gz'.format(subID, smooth_index)) 

# group-level analysis 
def second_level_glm(sublist): 

    glm_contrasts = {}
    contrast_decision_long = []
    contrast_decision_short = []

    contrast_decision_long_short = []
    contrast_decision_short_long = []


    for subID in sublist:
        contrast_decision_long.append(load_img('GLM2_results/{}/decision_long_pm_beta_smoothed.nii.gz'.format(subID)))
        contrast_decision_short.append(load_img('GLM2_results/{}/decision_short_pm_beta_smoothed.nii.gz'.format(subID)))
        contrast_decision_long_short.append(load_img('GLM2_results/{}/decision_long_short_pm_beta_smoothed.nii.gz'.format(subID)))
        contrast_decision_short_long.append(load_img('GLM2_results/{}/decision_short_long_pm_beta_smoothed.nii.gz'.format(subID)))
        
    glm_contrasts['decision_long_pm'] = contrast_decision_long
    glm_contrasts['decision_short_pm'] = contrast_decision_short
    glm_contrasts['decision_long_pm - decision_short_pm'] = contrast_decision_long_short
    glm_contrasts['decision_short_pm - decision_long_pm'] = contrast_decision_short_long
    
    gdesign_matrix = pd.DataFrame([1] * len(sublist), columns=["intercept"])
    
    # compute contrasts
    group_decision_long = SecondLevelModel()
    group_decision_long.fit(glm_contrasts['decision_long_pm'], design_matrix = gdesign_matrix)
    group_decision_long_output = group_decision_long.compute_contrast(output_type="all")
    
    group_decision_short = SecondLevelModel()
    group_decision_short.fit(glm_contrasts['decision_short_pm'], design_matrix = gdesign_matrix)
    group_decision_short_output = group_decision_short.compute_contrast(output_type="all")
    
    group_decision_long_short = SecondLevelModel()
    group_decision_long_short.fit(glm_contrasts['decision_long_pm - decision_short_pm'], design_matrix = gdesign_matrix)
    group_decision_long_short_output = group_decision_long_short.compute_contrast(output_type="all")
    
    group_decision_short_long = SecondLevelModel()
    group_decision_short_long.fit(glm_contrasts['decision_short_pm - decision_long_pm'], design_matrix = gdesign_matrix)
    group_decision_short_long_output = group_decision_short_long.compute_contrast(output_type="all")
    
    # correction
    thresholded_decision_long, threshold_decision_long = threshold_stats_img(
        group_decision_long_output["z_score"],
        alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
        cluster_threshold=30
    )
    
    thresholded_decision_short, threshold_decision_short = threshold_stats_img(
        group_decision_short_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_decision_long_short, threshold_decision_long_short = threshold_stats_img(
        group_decision_long_short_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_decision_short_long, threshold_decision_short_long = threshold_stats_img(
        group_decision_short_long_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )

    # saving model outputs
    if not os.path.exists('GLM2_results/group'):
        os.mkdir('GLM2_results/group')

    thresholded_decision_long.to_filename('GLM2_results/group/thresholded_decision_long_pm_zscore.nii.gz')
    decision_long_cluster_table = get_clusters_table(thresholded_decision_long, threshold_decision_long, cluster_threshold=30)
    decision_long_cluster_table.to_csv('GLM2_results/thresholded_decision_long_pm_cluster.csv')
    group_decision_long_output['z_score'].to_filename('GLM2_results/group/unthresholded_decision_long_pm_zscore.nii.gz')
    group_decision_long_report = make_glm_report(model = group_decision_long, contrasts ='intercept', 
                                                 alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_decision_long_report.save_as_html('GLM2_results/group/group_decision_long_pm.html')
    
    thresholded_decision_short.to_filename('GLM2_results/group/thresholded_decision_short_pm_zscore.nii.gz')
    decision_short_cluster_table = get_clusters_table(thresholded_decision_short, threshold_decision_short, cluster_threshold=30)
    decision_short_cluster_table.to_csv('GLM2_results/thresholded_decision_short_pm_cluster.csv')
    group_decision_short_output['z_score'].to_filename('GLM2_results/group/unthresholded_decision_short_pm_zscore.nii.gz')
    group_decision_short_report = make_glm_report(model = group_decision_short, contrasts ='intercept', 
                                                  alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_decision_short_report.save_as_html('GLM2_results/group/group_decision_short_pm.html')
      
    thresholded_decision_long_short.to_filename('GLM2_results/group/thresholded_decision_long_short_pm_zscore.nii.gz')
    decision_long_short_cluster_table = get_clusters_table(thresholded_decision_long_short, threshold_decision_long_short, cluster_threshold=30)
    decision_long_short_cluster_table.to_csv('GLM2_results/thresholded_decision_long_short_pm_cluster.csv')
    group_decision_long_short_output['z_score'].to_filename('GLM2_results/group/unthresholded_decision_long_short_pm_zscore.nii.gz')
    group_decision_long_short_report = make_glm_report(model = group_decision_long_short, contrasts ='intercept', 
                                                       alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_decision_long_short_report.save_as_html('GLM2_results/group/group_decision_long_short_pm.html')
    
    thresholded_decision_short_long.to_filename('GLM2_results/group/thresholded_decision_short_long_pm_zscore.nii.gz')
    decision_short_long_cluster_table = get_clusters_table(thresholded_decision_short_long, threshold_decision_short_long, cluster_threshold=30)
    decision_short_long_cluster_table.to_csv('GLM2_results/thresholded_decision_short_long_pm_cluster.csv')
    group_decision_short_long_output['z_score'].to_filename('GLM2_results/group/unthresholded_decision_short_long_pm_zscore.nii.gz')
    group_decision_short_long_report = make_glm_report(model = group_decision_short_long, contrasts ='intercept', 
                                                       alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_decision_short_long_report.save_as_html('GLM2_results/group/group_decision_short_long_pm.html')
    

if __name__ == '__main__':
    sublist = os.listdir('imgdata/') # specify the path where all preprocessed data are stored
    sublist.remove('.DS_Store') # for mac users to get rid of DS_store from the subject list
    sublist.sort()
        
    # fit first-level models, smoothed
    first_level_glm(sublist, smooth = 6)
    
    # fit second-level models
    second_level_glm(sublist)
 