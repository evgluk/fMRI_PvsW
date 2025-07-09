#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# codes of GLM1
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

# prepare event files
def event_maker(subID, runID):
    events_list = []
    colnames = ['onset', 'duration', 'intercept']
    for r in runID:
        decision_long = pd.read_csv('behavior_data/EV_contrast/GLM1/{}_LongDelay_fMRI_run-0{}_decision.tsv'.format(subID, r), 
                                    sep='\t', header = None, names = colnames, index_col=False) # specify your path accordingly
        confirmation_long = pd.read_csv('behavior_data/EV_contrast/GLM1/{}_LongDelay_fMRI_run-0{}_confirmation_end.tsv'.format(subID, r), 
                                    sep='\t', header = None, names = colnames, index_col=False) # specify your path accordingly
        decision_short = pd.read_csv('behavior_data/EV_contrast/GLM1/{}_ShortDelay_fMRI_run-0{}_decision.tsv'.format(subID, r), 
                                    sep='\t', header = None, names = colnames, index_col=False) # specify your path accordingly
        confirmation_short = pd.read_csv('behavior_data/EV_contrast/GLM1/{}_ShortDelay_fMRI_run-0{}_confirmation_end.tsv'.format(subID, r), 
                                    sep='\t', header = None, names = colnames, index_col=False) # specify your path accordingly
        decision_long['trial_type'] = 'decision_long'
        confirmation_long['trial_type'] = 'confirmation_long'
        decision_short['trial_type'] = 'decision_short'
        confirmation_short['trial_type'] = 'confirmation_short'
        
        events = pd.concat([decision_long, confirmation_long, decision_short, confirmation_short], ignore_index=True)
        events_list.append(events)
        
    return events_list

# prepare confounds files
def confounds_maker(subID, runID):
    confounds_list = []
    final_colnames = []
    
    for r in runID:
        confounds = pd.read_csv('imgdata/{}/func/{}_task-delay_run-0{}_desc-confounds_timeseries.tsv'.format(subID, subID, r),
                                 sep = '\t') # specify your path accordingly
        confoundscol = ['csf','white_matter', 'framewise_displacement', 'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'] + [i for i in list(confounds) if 'cosine' in i]
        confounds = confounds[confoundscol]
        confounds = confounds.fillna(0)
        
        colnames = list(confounds)
        if len(final_colnames) < len(colnames):
            final_colnames = colnames

        confounds_list.append(confounds)
    
    return confounds_list

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

# define all contrasts
def contrasts_maker(design_matrix):
    contrast_matrix = np.eye(design_matrix.shape[1])
    contrasts = {
        column: contrast_matrix[i]
        for i, column in enumerate(design_matrix.columns)
    }

    contrasts["decision_short - decision_long"] = (
        contrasts["decision_short"] - contrasts["decision_long"]
    )
    
    contrasts["decision_long - decision_short"] = (
        contrasts["decision_long"] - contrasts["decision_short"]
    )
    
    contrasts["confirmation_short - confirmation_long"] = (
        contrasts["confirmation_short"] - contrasts["confirmation_long"]
    )
    
    contrasts["confirmation_long - confirmation_short"] = (
        contrasts["confirmation_long"] - contrasts["confirmation_short"]
    )
   
    return contrasts
    
# individual-level analysis, loop over subjects
def first_level_glm(sublist, smooth):
    for subID in sublist:
        
        print('model fitting on {} is starting'.format(subID))
        
        # saving model outputs
        if not os.path.exists('GLM1_results'):
            os.mkdir('GLM1_results')
        directory = 'GLM1_results/{}'.format(subID)
        if not os.path.exists(directory):
            os.mkdir(directory)
        
        sub_imgs = []
        runID = read_runID(subID)
    
        for r in runID:
            func = load_img('imgdata/{}/func/{}_task-delay_run-0{}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'.format(subID, subID, r)) # specify your path accordingly
            sub_imgs.append(func)
             
        events_list = event_maker(subID, runID)
        confounds_list = confounds_maker(subID, runID)
        
        fmri_glm = FirstLevelModel(t_r = 1.74,
                                   noise_model = 'ar1',
                                   hrf_model = 'spm',
                                   drift_model = None, # I already have cosine values in confounds files
                                   signal_scaling = False,
                                   minimize_memory = False,
                                   smoothing_fwhm = smooth)
        
        fmri_glm = fmri_glm.fit(sub_imgs, events_list, confounds_list)
        matrix_list = fmri_glm.design_matrices_
    
        matrix = matrix_maker(matrix_list)
        contrasts = contrasts_maker(matrix)
        
        for m in range(len(matrix_list)):
            matrix_tosave = matrix_list[m]
            matrix_tosave.to_csv('GLM1_results/{}/design_matrix_run-0{}.csv'.format(subID, runID[m]), sep=',', index=False)
            plot_design_matrix(matrix_tosave, output_file = 'GLM1_results/{}/design_matrix_run-0{}.png'.format(subID, runID[m]))
    
        decision_long_output = fmri_glm.compute_contrast(
            contrasts['decision_long'],
            output_type="all",
        )
        
        decision_short_output = fmri_glm.compute_contrast(
            contrasts['decision_short'],
            output_type="all",
        )
        
        confirmation_long_output = fmri_glm.compute_contrast(
            contrasts['confirmation_long'],
            output_type="all",
        )
        
        confirmation_short_output = fmri_glm.compute_contrast(
            contrasts['confirmation_short'],
            output_type="all",
        )
        
        # long > short
        decision_long_short_output = fmri_glm.compute_contrast(
            contrasts['decision_long - decision_short'],
            output_type="all",
        )
        
        # short > long
        decision_short_long_output = fmri_glm.compute_contrast(
            contrasts['decision_short - decision_long'],
            output_type="all",
        )
        
        confirmation_long_short_output = fmri_glm.compute_contrast(
            contrasts['confirmation_long - confirmation_short'],
            output_type="all",
        )
        
        confirmation_short_long_output = fmri_glm.compute_contrast(
            contrasts['confirmation_short - confirmation_long'],
            output_type="all",
        )
        
        # saving model outputs
        if not os.path.exists('GLM1_results'):
            os.mkdir('GLM1_results')
        directory = 'GLM1_results/{}'.format(subID)
        if not os.path.exists(directory):
            os.mkdir(directory)
        
        if smooth == False:
            smooth_index = 'unsmoothed'
        else:
            smooth_index = 'smoothed'
            
        # beta values
        decision_long_output['effect_size'].to_filename('GLM1_results/{}/decision_long_beta_{}.nii.gz'.format(subID, smooth_index))
        decision_short_output['effect_size'].to_filename('GLM1_results/{}/decision_short_beta_{}.nii.gz'.format(subID, smooth_index)) 
        confirmation_long_output['effect_size'].to_filename('GLM1_results/{}/confirmation_long_beta_{}.nii.gz'.format(subID, smooth_index)) 
        confirmation_short_output['effect_size'].to_filename('GLM1_results/{}/confirmation_short_beta_{}.nii.gz'.format(subID, smooth_index)) 
        decision_long_short_output['effect_size'].to_filename('GLM1_results/{}/decision_long_short_beta_{}.nii.gz'.format(subID, smooth_index))
        decision_short_long_output['effect_size'].to_filename('GLM1_results/{}/decision_short_long_beta_{}.nii.gz'.format(subID, smooth_index)) 
        confirmation_long_short_output['effect_size'].to_filename('GLM1_results/{}/confirmation_long_short_beta_{}.nii.gz'.format(subID, smooth_index)) 
        confirmation_short_long_output['effect_size'].to_filename('GLM1_results/{}/confirmation_short_long_beta_{}.nii.gz'.format(subID, smooth_index)) 
        
        # z values
        decision_long_output['z_score'].to_filename('GLM1_results/{}/decision_long_zstat_{}.nii.gz'.format(subID, smooth_index))
        decision_short_output['z_score'].to_filename('GLM1_results/{}/decision_short_zstat_{}.nii.gz'.format(subID, smooth_index)) 
        confirmation_long_output['z_score'].to_filename('GLM1_results/{}/confirmation_long_zstat_{}.nii.gz'.format(subID, smooth_index)) 
        confirmation_short_output['z_score'].to_filename('GLM1_results/{}/confirmation_short_zstat_{}.nii.gz'.format(subID, smooth_index)) 
        decision_long_short_output['z_score'].to_filename('GLM1_results/{}/decision_long_short_zstat_{}.nii.gz'.format(subID, smooth_index))
        decision_short_long_output['z_score'].to_filename('GLM1_results/{}/decision_short_long_zstat_{}.nii.gz'.format(subID, smooth_index)) 
        confirmation_long_short_output['z_score'].to_filename('GLM1_results/{}/confirmation_long_short_zstat_{}.nii.gz'.format(subID, smooth_index)) 
        confirmation_short_long_output['z_score'].to_filename('GLM1_results/{}/confirmation_short_long_zstat_{}.nii.gz'.format(subID, smooth_index)) 


# group-level analysis 
def second_level_glm(sublist): 
    
    k_fits = pd.read_csv('behavior_data/fMRI_fits.csv', sep=',')
    k_fits = k_fits.sort_values(by = 'BIDS_ID')
    
    glm_contrasts = {}
    contrast_decision_long = []
    contrast_decision_short = []
    contrast_confirmation_long = []
    contrast_confirmation_short = []
    contrast_decision_long_short = []
    contrast_decision_short_long = []
    contrast_confirmation_long_short = []
    contrast_confirmation_short_long = []
    contrast_group_diff_SD = k_fits['scut'].replace(2, -1) # group similar - group different
    contrast_group_diff_DS = k_fits['scut'].replace(1, -1) # group different - group similar
    contrast_group_diff_DS = contrast_group_diff_DS.replace(2, 1) # group different - group similar
    contrast_group_diff_SD = contrast_group_diff_SD.tolist()
    contrast_group_diff_DS = contrast_group_diff_DS.tolist()

    for subID in sublist:
        contrast_decision_long.append(load_img('GLM1_results/{}/decision_long_beta_smoothed.nii.gz'.format(subID)))
        contrast_decision_short.append(load_img('GLM1_results/{}/decision_short_beta_smoothed.nii.gz'.format(subID)))
        contrast_confirmation_long.append(load_img('GLM1_results/{}/confirmation_long_beta_smoothed.nii.gz'.format(subID)))
        contrast_confirmation_short.append(load_img('GLM1_results/{}/confirmation_short_beta_smoothed.nii.gz'.format(subID)))
        contrast_decision_long_short.append(load_img('GLM1_results/{}/decision_long_short_beta_smoothed.nii.gz'.format(subID)))
        contrast_decision_short_long.append(load_img('GLM1_results/{}/decision_short_long_beta_smoothed.nii.gz'.format(subID)))
        contrast_confirmation_long_short.append(load_img('GLM1_results/{}/confirmation_long_short_beta_smoothed.nii.gz'.format(subID)))
        contrast_confirmation_short_long.append(load_img('GLM1_results/{}/confirmation_short_long_beta_smoothed.nii.gz'.format(subID)))
        
    glm_contrasts['decision_long'] = contrast_decision_long
    glm_contrasts['decision_short'] = contrast_decision_short
    glm_contrasts['confirmation_long'] = contrast_confirmation_long
    glm_contrasts['confirmation_short'] = contrast_confirmation_short
    glm_contrasts['decision_long - decision_short'] = contrast_decision_long_short
    glm_contrasts['decision_short - decision_long'] = contrast_decision_short_long
    glm_contrasts['confirmation_long - confirmation_short'] = contrast_confirmation_long_short
    glm_contrasts['confirmation_short - confirmation_long'] = contrast_confirmation_short_long
    
    gdesign_matrix = pd.DataFrame([1] * len(sublist), columns=["intercept"])
    gdesign_group_diff_SD_matrix = pd.DataFrame(contrast_group_diff_SD, columns=["intercept"])
    gdesign_group_diff_DS_matrix = pd.DataFrame(contrast_group_diff_DS, columns=["intercept"])
    
    # compute contrasts
    group_decision_long = SecondLevelModel()
    group_decision_long.fit(glm_contrasts['decision_long'], design_matrix = gdesign_matrix)
    group_decision_long_output = group_decision_long.compute_contrast(output_type="all")
    
    group_decision_short = SecondLevelModel()
    group_decision_short.fit(glm_contrasts['decision_short'], design_matrix = gdesign_matrix)
    group_decision_short_output = group_decision_short.compute_contrast(output_type="all")
    
    group_confirmation_long = SecondLevelModel()
    group_confirmation_long.fit(glm_contrasts['confirmation_long'], design_matrix = gdesign_matrix)
    group_confirmation_long_output = group_confirmation_long.compute_contrast(output_type="all")
    
    group_confirmation_short = SecondLevelModel()
    group_confirmation_short.fit(glm_contrasts['confirmation_short'], design_matrix = gdesign_matrix)
    group_confirmation_short_output = group_confirmation_short.compute_contrast(output_type="all")
    
    group_decision_long_short = SecondLevelModel()
    group_decision_long_short.fit(glm_contrasts['decision_long - decision_short'], design_matrix = gdesign_matrix)
    group_decision_long_short_output = group_decision_long_short.compute_contrast(output_type="all")
    
    group_decision_short_long = SecondLevelModel()
    group_decision_short_long.fit(glm_contrasts['decision_short - decision_long'], design_matrix = gdesign_matrix)
    group_decision_short_long_output = group_decision_short_long.compute_contrast(output_type="all")
    
    group_confirmation_long_short = SecondLevelModel()
    group_confirmation_long_short.fit(glm_contrasts['confirmation_long - confirmation_short'], design_matrix = gdesign_matrix)
    group_confirmation_long_short_output = group_confirmation_long_short.compute_contrast(output_type="all")
    
    group_confirmation_short_long = SecondLevelModel()
    group_confirmation_short_long.fit(glm_contrasts['confirmation_short - confirmation_long'], design_matrix = gdesign_matrix)
    group_confirmation_short_long_output = group_confirmation_short_long.compute_contrast(output_type="all")
    
    # group diffrence, similar - differnt
    group_diff_SD_decision_long_short = SecondLevelModel()
    group_diff_SD_decision_long_short.fit(glm_contrasts['decision_long - decision_short'], design_matrix = gdesign_group_diff_SD_matrix)
    group_diff_SD_decision_long_short_output = group_diff_SD_decision_long_short.compute_contrast(output_type="all")
    
    group_diff_SD_decision_short_long = SecondLevelModel()
    group_diff_SD_decision_short_long.fit(glm_contrasts['decision_short - decision_long'], design_matrix = gdesign_group_diff_SD_matrix)
    group_diff_SD_decision_short_long_output = group_diff_SD_decision_short_long.compute_contrast(output_type="all")
    
    group_diff_SD_confirmation_long_short = SecondLevelModel()
    group_diff_SD_confirmation_long_short.fit(glm_contrasts['confirmation_long - confirmation_short'], design_matrix = gdesign_group_diff_SD_matrix)
    group_diff_SD_confirmation_long_short_output = group_diff_SD_confirmation_long_short.compute_contrast(output_type="all")
    
    group_diff_SD_confirmation_short_long = SecondLevelModel()
    group_diff_SD_confirmation_short_long.fit(glm_contrasts['confirmation_short - confirmation_long'], design_matrix = gdesign_group_diff_SD_matrix)
    group_diff_SD_confirmation_short_long_output = group_diff_SD_confirmation_short_long.compute_contrast(output_type="all")

    # group diffrence, differnt - similar
    group_diff_DS_decision_long_short = SecondLevelModel()
    group_diff_DS_decision_long_short.fit(glm_contrasts['decision_long - decision_short'], design_matrix = gdesign_group_diff_DS_matrix)
    group_diff_DS_decision_long_short_output = group_diff_DS_decision_long_short.compute_contrast(output_type="all")
    
    group_diff_DS_decision_short_long = SecondLevelModel()
    group_diff_DS_decision_short_long.fit(glm_contrasts['decision_short - decision_long'], design_matrix = gdesign_group_diff_DS_matrix)
    group_diff_DS_decision_short_long_output = group_diff_DS_decision_short_long.compute_contrast(output_type="all")
    
    group_diff_DS_confirmation_long_short = SecondLevelModel()
    group_diff_DS_confirmation_long_short.fit(glm_contrasts['confirmation_long - confirmation_short'], design_matrix = gdesign_group_diff_DS_matrix)
    group_diff_DS_confirmation_long_short_output = group_diff_DS_confirmation_long_short.compute_contrast(output_type="all")
    
    group_diff_DS_confirmation_short_long = SecondLevelModel()
    group_diff_DS_confirmation_short_long.fit(glm_contrasts['confirmation_short - confirmation_long'], design_matrix = gdesign_group_diff_DS_matrix)
    group_diff_DS_confirmation_short_long_output = group_diff_DS_confirmation_short_long.compute_contrast(output_type="all")

    
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
    
    thresholded_confirmation_long, threshold_confirmation_long = threshold_stats_img(
        group_confirmation_long_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_confirmation_short, threshold_confirmation_short = threshold_stats_img(
        group_confirmation_short_output["z_score"],
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
    
    thresholded_confirmation_long_short, threshold_confirmation_long_short = threshold_stats_img(
        group_confirmation_long_short_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_confirmation_short_long, threshold_confirmation_short_long = threshold_stats_img(
        group_confirmation_short_long_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_group_diff_SD_decision_long_short, threshold_group_diff_SD_decision_long_short = threshold_stats_img(
        group_diff_SD_decision_long_short_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_group_diff_SD_decision_short_long, threshold_group_diff_SD_decision_short_long = threshold_stats_img(
        group_diff_SD_decision_short_long_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_group_diff_SD_confirmation_long_short, threshold_group_diff_SD_confirmation_long_short = threshold_stats_img(
        group_diff_SD_confirmation_long_short_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_group_diff_SD_confirmation_short_long, threshold_group_diff_SD_confirmation_short_long = threshold_stats_img(
        group_diff_SD_confirmation_short_long_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_group_diff_DS_decision_long_short, threshold_group_diff_DS_decision_long_short = threshold_stats_img(
        group_diff_DS_decision_long_short_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_group_diff_DS_decision_short_long, threshold_group_diff_DS_decision_short_long = threshold_stats_img(
        group_diff_DS_decision_short_long_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_group_diff_DS_confirmation_long_short, threshold_group_diff_DS_confirmation_long_short = threshold_stats_img(
        group_diff_DS_confirmation_long_short_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    thresholded_group_diff_DS_confirmation_short_long, threshold_group_diff_DS_confirmation_short_long = threshold_stats_img(
        group_diff_DS_confirmation_short_long_output["z_score"],
        alpha=0.05, height_control="fdr",
        cluster_threshold=30
    )
    
    # saving model outputs
    if not os.path.exists('GLM1_results/group'):
        os.mkdir('GLM1_results/group')

    thresholded_decision_long.to_filename('GLM1_results/group/thresholded_decision_long_zscore.nii.gz')
    decision_long_cluster_table = get_clusters_table(thresholded_decision_long, threshold_decision_long, cluster_threshold=30)
    decision_long_cluster_table.to_csv('GLM1_results/thresholded_decision_long_cluster.csv')
    group_decision_long_output['z_score'].to_filename('GLM1_results/group/unthresholded_decision_long_zscore.nii.gz')
    group_decision_long_report = make_glm_report(model = group_decision_long, contrasts ='intercept', 
                                                 alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_decision_long_report.save_as_html('GLM1_results/group/group_decision_long.html')
    
    thresholded_decision_short.to_filename('GLM1_results/group/thresholded_decision_short_zscore.nii.gz')
    decision_short_cluster_table = get_clusters_table(thresholded_decision_short, threshold_decision_short, cluster_threshold=30)
    decision_short_cluster_table.to_csv('GLM1_results/thresholded_decision_short_cluster.csv')
    group_decision_short_output['z_score'].to_filename('GLM1_results/group/unthresholded_decision_short_zscore.nii.gz')
    group_decision_short_report = make_glm_report(model = group_decision_short, contrasts ='intercept', 
                                                  alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_decision_short_report.save_as_html('GLM1_results/group/group_decision_short.html')
    
    thresholded_confirmation_long.to_filename('GLM1_results/group/thresholded_confirmation_long_zscore.nii.gz')
    confirmation_long_cluster_table = get_clusters_table(thresholded_confirmation_long, threshold_confirmation_long, cluster_threshold=30)
    confirmation_long_cluster_table.to_csv('GLM1_results/thresholded_confirmation_long_cluster.csv')
    group_confirmation_long_output['z_score'].to_filename('GLM1_results/group/unthresholded_confirmation_long_zscore.nii.gz')
    group_confirmation_long_report = make_glm_report(model = group_confirmation_long, contrasts ='intercept', 
                                                     alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_confirmation_long_report.save_as_html('GLM1_results/group/group_confirmation_long.html')

    thresholded_confirmation_short.to_filename('GLM1_results/group/thresholded_confirmation_short_zscore.nii.gz')
    confirmation_short_cluster_table = get_clusters_table(thresholded_confirmation_short, threshold_confirmation_short, cluster_threshold=30)
    confirmation_short_cluster_table.to_csv('GLM1_results/thresholded_confirmation_short_cluster.csv')
    group_confirmation_short_output['z_score'].to_filename('GLM1_results/group/unthresholded_confirmation_short_zscore.nii.gz')
    group_confirmation_short_report = make_glm_report(model = group_confirmation_short, contrasts ='intercept', 
                                                      alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_confirmation_short_report.save_as_html('GLM1_results/group/group_confirmation_short.html')
    
    thresholded_decision_long_short.to_filename('GLM1_results/group/thresholded_decision_long_short_zscore.nii.gz')
    decision_long_short_cluster_table = get_clusters_table(thresholded_decision_long_short, threshold_decision_long_short, cluster_threshold=30)
    decision_long_short_cluster_table.to_csv('GLM1_results/thresholded_decision_long_short_cluster.csv')
    group_decision_long_short_output['z_score'].to_filename('GLM1_results/group/unthresholded_decision_long_short_zscore.nii.gz')
    group_decision_long_short_report = make_glm_report(model = group_decision_long_short, contrasts ='intercept', 
                                                       alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_decision_long_short_report.save_as_html('GLM1_results/group/group_decision_long_short.html')
    
    thresholded_decision_short_long.to_filename('GLM1_results/group/thresholded_decision_short_long_zscore.nii.gz')
    decision_short_long_cluster_table = get_clusters_table(thresholded_decision_short_long, threshold_decision_short_long, cluster_threshold=30)
    decision_short_long_cluster_table.to_csv('GLM1_results/thresholded_decision_short_long_cluster.csv')
    group_decision_short_long_output['z_score'].to_filename('GLM1_results/group/unthresholded_decision_short_long_zscore.nii.gz')
    group_decision_short_long_report = make_glm_report(model = group_decision_short_long, contrasts ='intercept', 
                                                       alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_decision_short_long_report.save_as_html('GLM1_results/group/group_decision_short_long.html')
    
    thresholded_confirmation_long_short.to_filename('GLM1_results/group/thresholded_confirmation_long_short_zscore.nii.gz')
    confirmation_long_short_cluster_table = get_clusters_table(thresholded_confirmation_long_short, threshold_confirmation_long_short, cluster_threshold=30)
    confirmation_long_short_cluster_table.to_csv('GLM1_results/thresholded_confirmation_long_short_cluster.csv')
    group_confirmation_long_short_output['z_score'].to_filename('GLM1_results/group/unthresholded_confirmation_long_short_zscore.nii.gz')
    group_confirmation_long_short_report = make_glm_report(model = group_confirmation_long_short, contrasts ='intercept', 
                                                           alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_confirmation_long_short_report.save_as_html('GLM1_results/group/group_confirmation_long_short.html')
    
    thresholded_confirmation_short_long.to_filename('GLM1_results/group/thresholded_confirmation_short_long_zscore.nii.gz')
    confirmation_short_long_cluster_table = get_clusters_table(thresholded_confirmation_short_long, threshold_confirmation_short_long, cluster_threshold=30)
    confirmation_short_long_cluster_table.to_csv('GLM1_results/thresholded_confirmation_short_long_cluster.csv')
    group_confirmation_short_long_output['z_score'].to_filename('GLM1_results/group/unthresholded_confirmation_short_long_zscore.nii.gz')
    group_confirmation_short_long_report = make_glm_report(model = group_confirmation_short_long, contrasts ='intercept', 
                                                           alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_confirmation_short_long_report.save_as_html('GLM1_results/group/group_confirmation_short_long.html')
    
    thresholded_group_diff_SD_decision_long_short.to_filename('GLM1_results/group/thresholded_group_diff_SD_decision_long_short_zscore.nii.gz')
    group_diff_SD_decision_long_short_cluster_table = get_clusters_table(thresholded_group_diff_SD_decision_long_short, threshold_group_diff_SD_decision_long_short, cluster_threshold=30)
    group_diff_SD_decision_long_short_cluster_table.to_csv('GLM1_results/thresholded_group_diff_SD_decision_long_short_cluster.csv')
    group_diff_SD_decision_long_short_output['z_score'].to_filename('GLM1_results/group/unthresholded_group_diff_SD_decision_long_short_zscore.nii.gz')
    group_diff_SD_decision_long_short_report = make_glm_report(model = group_diff_SD_decision_long_short, contrasts ='intercept', 
                                                       alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_diff_SD_decision_long_short_report.save_as_html('GLM1_results/group/group_diff_SD_decision_long_short.html')
    
    thresholded_group_diff_SD_decision_short_long.to_filename('GLM1_results/group/thresholded_group_diff_SD_decision_short_long_zscore.nii.gz')
    group_diff_SD_decision_short_long_cluster_table = get_clusters_table(thresholded_group_diff_SD_decision_short_long, threshold_group_diff_SD_decision_short_long, cluster_threshold=30)
    group_diff_SD_decision_short_long_cluster_table.to_csv('GLM1_results/thresholded_group_diff_SD_decision_short_long_cluster.csv')
    group_diff_SD_decision_short_long_output['z_score'].to_filename('GLM1_results/group/unthresholded_group_diff_SD_decision_short_long_zscore.nii.gz')
    group_diff_SD_decision_short_long_report = make_glm_report(model = group_diff_SD_decision_short_long, contrasts ='intercept', 
                                                       alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_diff_SD_decision_short_long_report.save_as_html('GLM1_results/group/group_diff_SD_decision_short_long.html')
    
    thresholded_group_diff_SD_confirmation_long_short.to_filename('GLM1_results/group/thresholded_group_diff_SD_confirmation_long_short_zscore.nii.gz')
    group_diff_SD_confirmation_long_short_cluster_table = get_clusters_table(thresholded_group_diff_SD_confirmation_long_short, threshold_group_diff_SD_confirmation_long_short, cluster_threshold=30)
    group_diff_SD_confirmation_long_short_cluster_table.to_csv('GLM1_results/thresholded_group_diff_SD_confirmation_long_short_cluster.csv')
    group_diff_SD_confirmation_long_short_output['z_score'].to_filename('GLM1_results/group/unthresholded_group_diff_SD_confirmation_long_short_zscore.nii.gz')
    group_diff_SD_confirmation_long_short_report = make_glm_report(model = group_diff_SD_confirmation_long_short, contrasts ='intercept', 
                                                           alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_diff_SD_confirmation_long_short_report.save_as_html('GLM1_results/group/group_diff_SD_confirmation_long_short.html')
    
    thresholded_group_diff_SD_confirmation_short_long.to_filename('GLM1_results/group/thresholded_group_diff_SD_confirmation_short_long_zscore.nii.gz')
    group_diff_SD_confirmation_short_long_cluster_table = get_clusters_table(thresholded_group_diff_SD_confirmation_short_long, threshold_group_diff_SD_confirmation_short_long, cluster_threshold=30)
    group_diff_SD_confirmation_short_long_cluster_table.to_csv('GLM1_results/thresholded_group_diff_SD_confirmation_short_long_cluster.csv')
    group_diff_SD_confirmation_short_long_output['z_score'].to_filename('GLM1_results/group/unthresholded_group_diff_SD_confirmation_short_long_zscore.nii.gz')
    group_diff_SD_confirmation_short_long_report = make_glm_report(model = group_diff_SD_confirmation_short_long, contrasts ='intercept', 
                                                           alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_diff_SD_confirmation_short_long_report.save_as_html('GLM1_results/group/group_diff_SD_confirmation_short_long.html')
    
    thresholded_group_diff_DS_decision_long_short.to_filename('GLM1_results/group/thresholded_group_diff_DS_decision_long_short_zscore.nii.gz')
    group_diff_DS_decision_long_short_cluster_table = get_clusters_table(thresholded_group_diff_DS_decision_long_short, threshold_group_diff_DS_decision_long_short, cluster_threshold=30)
    group_diff_DS_decision_long_short_cluster_table.to_csv('GLM1_results/thresholded_group_diff_DS_decision_long_short_cluster.csv')
    group_diff_DS_decision_long_short_output['z_score'].to_filename('GLM1_results/group/unthresholded_group_diff_DS_decision_long_short_zscore.nii.gz')
    group_diff_DS_decision_long_short_report = make_glm_report(model = group_diff_DS_decision_long_short, contrasts ='intercept', 
                                                       alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_diff_DS_decision_long_short_report.save_as_html('GLM1_results/group/group_diff_DS_decision_long_short.html')
    
    thresholded_group_diff_DS_decision_short_long.to_filename('GLM1_results/group/thresholded_group_diff_DS_decision_short_long_zscore.nii.gz')
    group_diff_DS_decision_short_long_cluster_table = get_clusters_table(thresholded_group_diff_DS_decision_short_long, threshold_group_diff_DS_decision_short_long, cluster_threshold=30)
    group_diff_DS_decision_short_long_cluster_table.to_csv('GLM1_results/thresholded_group_diff_DS_decision_short_long_cluster.csv')
    group_diff_DS_decision_short_long_output['z_score'].to_filename('GLM1_results/group/unthresholded_group_diff_DS_decision_short_long_zscore.nii.gz')
    group_diff_DS_decision_short_long_report = make_glm_report(model = group_diff_DS_decision_short_long, contrasts ='intercept', 
                                                       alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_diff_DS_decision_short_long_report.save_as_html('GLM1_results/group/group_diff_DS_decision_short_long.html')
    
    thresholded_group_diff_DS_confirmation_long_short.to_filename('GLM1_results/group/thresholded_group_diff_DS_confirmation_long_short_zscore.nii.gz')
    group_diff_DS_confirmation_long_short_cluster_table = get_clusters_table(thresholded_group_diff_DS_confirmation_long_short, threshold_group_diff_DS_confirmation_long_short, cluster_threshold=30)
    group_diff_DS_confirmation_long_short_cluster_table.to_csv('GLM1_results/thresholded_group_diff_DS_confirmation_long_short_cluster.csv')
    group_diff_DS_confirmation_long_short_output['z_score'].to_filename('GLM1_results/group/unthresholded_group_diff_DS_confirmation_long_short_zscore.nii.gz')
    group_diff_DS_confirmation_long_short_report = make_glm_report(model = group_diff_DS_confirmation_long_short, contrasts ='intercept', 
                                                           alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_diff_DS_confirmation_long_short_report.save_as_html('GLM1_results/group/group_diff_DS_confirmation_long_short.html')
    
    thresholded_group_diff_DS_confirmation_short_long.to_filename('GLM1_results/group/thresholded_group_diff_DS_confirmation_short_long_zscore.nii.gz')
    group_diff_DS_confirmation_short_long_cluster_table = get_clusters_table(thresholded_group_diff_DS_confirmation_short_long, threshold_group_diff_DS_confirmation_short_long, cluster_threshold=30)
    group_diff_DS_confirmation_short_long_cluster_table.to_csv('GLM1_results/thresholded_group_diff_DS_confirmation_short_long_cluster.csv')
    group_diff_DS_confirmation_short_long_output['z_score'].to_filename('GLM1_results/group/unthresholded_group_diff_DS_confirmation_short_long_zscore.nii.gz')
    group_diff_DS_confirmation_short_long_report = make_glm_report(model = group_diff_DS_confirmation_short_long, contrasts ='intercept', 
                                                           alpha=0.05, height_control="fdr", cluster_threshold=30)
    group_diff_DS_confirmation_short_long_report.save_as_html('GLM1_results/group/group_diff_DS_confirmation_short_long.html')
    
if __name__ == '__main__':
    sublist = os.listdir('imgdata/') # specify the path where all preprocessed data are stored
    sublist.remove('.DS_Store') # for mac users to get rid of DS_store from the subject list
    sublist.sort()
    
    # fit first-level models, unsmoothed
    first_level_glm(sublist, smooth = False)
    
    # fit first-level models, smoothed
    first_level_glm(sublist, smooth = 6)
    
    # fit second-level models
    second_level_glm(sublist)
