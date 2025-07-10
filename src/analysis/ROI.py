#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# codes for ROI
# =============================================================================
import nibabel as nib
from nilearn.maskers import NiftiMasker
from nilearn.image import resample_to_img
from nilearn.glm.thresholding import threshold_stats_img
import os
import pandas as pd
from scipy.stats import pearsonr
from scipy.stats import sem
from scipy.stats import ttest_1samp
from scipy.stats import ttest_ind
import numpy as np 

# Resample the ROI mask to match the functional image
func = nib.load('imgdata/sub-001/func/sub-001_task-delay_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
raw_mask = nib.load('Bartra3A_and_Clithero3_meta_mask.nii')
mask = resample_to_img(raw_mask, func, interpolation='nearest')
masker = NiftiMasker(mask_img = mask)

# GLM1
GLM1_corr_table = pd.DataFrame(columns=['subID', 'corr', 'p', 'mean_long', 'mean_short'])
GLM1_path = 'GLM1_results/'
subjlist = [x for x, _, _ in os.walk(GLM1_path) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)

for s in range(nsub):
    subjpath = subjlist[s]
    GLM1_decision_long = nib.load(subjpath + '/decision_long_zstat_smoothed.nii.gz')
    GLM1_decision_short = nib.load(subjpath + '/decision_short_zstat_smoothed.nii.gz')
    
    GLM1_decision_long_masked = masker.fit_transform(GLM1_decision_long).squeeze()
    GLM1_decision_short_masked = masker.fit_transform(GLM1_decision_short).squeeze()
    
    corr = pearsonr(GLM1_decision_long_masked, GLM1_decision_short_masked)
    
    GLM1_corr_table.loc[s] = [subjpath[-7:], corr[0], corr[1], 
                              np.mean(GLM1_decision_long_masked),
                              np.mean(GLM1_decision_short_masked)]
    
mean_corr = np.nanmean(GLM1_corr_table['corr'])
upper_ci = mean_corr + 1.96 * sem(GLM1_corr_table['corr'], nan_policy = 'omit')
lower_ci = mean_corr - 1.96 * sem(GLM1_corr_table['corr'], nan_policy = 'omit')

# discount factor similarity group assignment
k_fits = pd.read_csv('behavior_data/fMRI_fits.csv', sep=',')
k_fits = k_fits.sort_values(by = 'BIDS_ID')
close_group = k_fits[k_fits['scut'] == 1]['BIDS_ID'].tolist()
far_group = k_fits[k_fits['scut'] == 2]['BIDS_ID'].tolist()
    
# GLM2, decision
GLM2_path_decision = 'GLM2_results_nilearn/' # decision, matrix generated in a nilearn manner

# selecting peak voxels
GLM2_unthreshold_decision_long = nib.load(GLM2_path_decision + 'group/unthresholded_decision_long_pm_zscore.nii.gz')
GLM2_unthreshold_decision_short = nib.load(GLM2_path_decision + 'group/unthresholded_decision_short_pm_zscore.nii.gz')

GLM2_decision_long_raw_mask, GLM2_decision_long_threshold = threshold_stats_img(
    GLM2_unthreshold_decision_long, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

GLM2_decision_short_raw_mask, GLM2_decision_short_threshold = threshold_stats_img(
    GLM2_unthreshold_decision_short, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

# making integrated mask, peak voxel + valuation
GLM2_decision_long_raw_mask_data = GLM2_decision_long_raw_mask.get_fdata()
GLM2_decision_long_raw_mask_ = (GLM2_decision_long_raw_mask_data > GLM2_decision_long_threshold).astype(np.uint8)
GLM2_decision_long_len = len(GLM2_decision_long_raw_mask_[GLM2_decision_long_raw_mask_==1]) # number of surviving voxels
GLM2_decision_long_mask = nib.Nifti1Image(GLM2_decision_long_raw_mask_, 
                                           affine=GLM2_unthreshold_decision_long.affine, 
                                           header=GLM2_unthreshold_decision_long.header)

GLM2_decision_short_raw_mask_data = GLM2_decision_short_raw_mask.get_fdata()
GLM2_decision_short_raw_mask_ = (GLM2_decision_short_raw_mask_data > GLM2_decision_short_threshold).astype(np.uint8)
GLM2_decision_short_len = len(GLM2_decision_short_raw_mask_[GLM2_decision_short_raw_mask_==1]) # number of surviving voxels
GLM2_decision_short_mask = nib.Nifti1Image(GLM2_decision_short_raw_mask_, 
                                           affine=GLM2_unthreshold_decision_short.affine, 
                                           header=GLM2_unthreshold_decision_short.header)

GLM2_decision_long_masker = NiftiMasker(mask_img = GLM2_decision_long_mask)
GLM2_decision_short_masker = NiftiMasker(mask_img = GLM2_decision_short_mask)

subjlist = [x for x, _, _ in os.walk(GLM2_path_decision) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM2_decision_long_pe = np.empty((nsub, GLM2_decision_long_len)) 
GLM2_decision_short_pe = np.empty((nsub, GLM2_decision_short_len))
GLM2_decision_long_close = np.empty((len(close_group), GLM2_decision_long_len))
GLM2_decision_short_close = np.empty((len(close_group), GLM2_decision_short_len))
GLM2_decision_long_far = np.empty((len(far_group), GLM2_decision_long_len))
GLM2_decision_short_far = np.empty((len(far_group), GLM2_decision_short_len))
close_index = 0
far_index = 0

for s in range(nsub):
    subjpath = subjlist[s]
    GLM2_decision_long = nib.load(subjpath + '/decision_long_pm_beta_smoothed.nii.gz')
    GLM2_decision_short = nib.load(subjpath + '/decision_short_pm_beta_smoothed.nii.gz')
    
    # GLM2_decision_long_masked = GLM2_decision_long_masker.fit_transform(GLM2_decision_long).squeeze()
    GLM2_decision_short_masked = GLM2_decision_short_masker.fit_transform(GLM2_decision_short).squeeze()
    
    # GLM2_decision_long_pe[s,:] =  GLM2_decision_long_masked
    GLM2_decision_short_pe[s,:] =  GLM2_decision_short_masked
    
    if subjpath[-7:] in close_group:
        # GLM2_decision_long_close[close_index,:] = GLM2_decision_long_masked
        GLM2_decision_short_close[close_index,:] = GLM2_decision_short_masked
        close_index += 1
    elif subjpath[-7:] in far_group:
        # GLM2_decision_long_far[far_index,:] = GLM2_decision_long_masked
        GLM2_decision_short_far[far_index,:] = GLM2_decision_short_masked
        far_index += 1
         
# GLM2_decision_long_mean = GLM2_decision_long_pe.mean(axis=(0))
GLM2_decision_short_mean = GLM2_decision_short_pe.mean(axis=(0))
# GLM2_decision_long_close_mean = GLM2_decision_long_close.mean(axis=(0))
GLM2_decision_short_close_mean = GLM2_decision_short_close.mean(axis=(0))
# GLM2_decision_long_far_mean = GLM2_decision_long_far.mean(axis=(0))
GLM2_decision_short_far_mean = GLM2_decision_short_far.mean(axis=(0))

# GLM2_decision_long_t_test = ttest_1samp(GLM2_decision_long_mean, 0)
GLM2_decision_short_t_test = ttest_1samp(GLM2_decision_short_mean, 0)
# GLM2_decision_long_far_close_t_test = ttest_ind(GLM2_decision_long_close_mean,
                                                # GLM2_decision_long_far_mean)
GLM2_decision_short_far_close_t_test = ttest_ind(GLM2_decision_short_close_mean,
                                                 GLM2_decision_short_far_mean)

    
# GLM2, confirmation
GLM2_path_confirmation = 'GLM2_results_confirmation/' # decision, matrix generated in a nilearn manner

# selecting peak voxels
GLM2_unthreshold_confirmation_long = nib.load(GLM2_path_confirmation + 'group/unthresholded_confirmation_long_pm_zscore.nii.gz')
GLM2_unthreshold_confirmation_short = nib.load(GLM2_path_confirmation + 'group/unthresholded_confirmation_short_pm_zscore.nii.gz')

GLM2_confirmation_long_raw_mask, GLM2_confirmation_long_threshold = threshold_stats_img(
    GLM2_unthreshold_confirmation_long, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

GLM2_confirmation_short_raw_mask, GLM2_confirmation_short_threshold = threshold_stats_img(
    GLM2_unthreshold_confirmation_short, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

# making integrated mask, peak voxel + valuation
GLM2_confirmation_long_raw_mask_data = GLM2_confirmation_long_raw_mask.get_fdata()
GLM2_confirmation_long_raw_mask_ = (GLM2_confirmation_long_raw_mask_data > GLM2_confirmation_long_threshold).astype(np.uint8)
GLM2_confirmation_long_len = len(GLM2_confirmation_long_raw_mask_[GLM2_confirmation_long_raw_mask_==1]) # number of surviving voxel
GLM2_confirmation_long_mask = nib.Nifti1Image(GLM2_confirmation_long_raw_mask_, 
                                           affine=GLM2_unthreshold_confirmation_long.affine, 
                                           header=GLM2_unthreshold_confirmation_long.header)

GLM2_confirmation_short_raw_mask_data = GLM2_confirmation_short_raw_mask.get_fdata()
GLM2_confirmation_short_raw_mask_ = (GLM2_confirmation_short_raw_mask_data > GLM2_confirmation_short_threshold).astype(np.uint8)
GLM2_confirmation_short_len = len(GLM2_confirmation_short_raw_mask_[GLM2_confirmation_short_raw_mask_==1]) # number of surviving voxel
GLM2_confirmation_short_mask = nib.Nifti1Image(GLM2_confirmation_short_raw_mask_, 
                                           affine=GLM2_unthreshold_confirmation_short.affine, 
                                           header=GLM2_unthreshold_confirmation_short.header)

GLM2_confirmation_long_masker = NiftiMasker(mask_img = GLM2_confirmation_long_mask)
GLM2_confirmation_short_masker = NiftiMasker(mask_img = GLM2_confirmation_short_mask)

subjlist = [x for x, _, _ in os.walk(GLM2_path_confirmation) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM2_confirmation_long_pe = np.empty((nsub, GLM2_confirmation_long_len))
GLM2_confirmation_short_pe = np.empty((nsub, GLM2_confirmation_short_len))
GLM2_confirmation_long_close = np.empty((len(close_group), GLM2_confirmation_long_len))
GLM2_confirmation_short_close = np.empty((len(close_group), GLM2_confirmation_short_len))
GLM2_confirmation_long_far = np.empty((len(far_group), GLM2_confirmation_long_len))
GLM2_confirmation_short_far = np.empty((len(far_group), GLM2_confirmation_short_len))
close_index = 0
far_index = 0

for s in range(nsub):
    subjpath = subjlist[s]
    GLM2_confirmation_long = nib.load(subjpath + '/confirmation_long_pm_beta_smoothed.nii.gz')
    GLM2_confirmation_short = nib.load(subjpath + '/confirmation_short_pm_beta_smoothed.nii.gz')
    
    GLM2_confirmation_long_masked = GLM2_confirmation_long_masker.fit_transform(GLM2_confirmation_long).squeeze()
    GLM2_confirmation_short_masked = GLM2_confirmation_short_masker.fit_transform(GLM2_confirmation_short).squeeze()
    
    GLM2_confirmation_long_pe[s,:] =  GLM2_confirmation_long_masked
    GLM2_confirmation_short_pe[s,:] =  GLM2_confirmation_short_masked
    
    if subjpath[-7:] in close_group:
        GLM2_confirmation_long_close[close_index,:] = GLM2_confirmation_long_masked
        GLM2_confirmation_short_close[close_index,:] = GLM2_confirmation_short_masked
        close_index += 1
    elif subjpath[-7:] in far_group:
        GLM2_confirmation_long_far[far_index,:] = GLM2_confirmation_long_masked
        GLM2_confirmation_short_far[far_index,:] = GLM2_confirmation_short_masked
        far_index += 1
    
GLM2_confirmation_long_mean = GLM2_confirmation_long_pe.mean(axis=(0))
GLM2_confirmation_short_mean = GLM2_confirmation_short_pe.mean(axis=(0))
GLM2_confirmation_long_close_mean = GLM2_confirmation_long_close.mean(axis=(0))
GLM2_confirmation_short_close_mean = GLM2_confirmation_short_close.mean(axis=(0))
GLM2_confirmation_long_far_mean = GLM2_confirmation_long_far.mean(axis=(0))
GLM2_confirmation_short_far_mean = GLM2_confirmation_short_far.mean(axis=(0))

GLM2_confirmation_long_t_test = ttest_1samp(GLM2_confirmation_long_mean, 0)
GLM2_confirmation_short_t_test = ttest_1samp(GLM2_confirmation_short_mean, 0) 
GLM2_confirmation_long_far_close_t_test = ttest_ind(GLM2_confirmation_long_close_mean,
                                                    GLM2_confirmation_long_far_mean)
GLM2_confirmation_short_far_close_t_test = ttest_ind(GLM2_confirmation_short_close_mean,
                                                     GLM2_confirmation_short_far_mean)
   

# GLM3, decision
GLM3_path_decision = 'GLM3_results_nilearn/' # decision, matrix generated in a nilearn manner

# selecting peak voxels
GLM3_unthreshold_decision_long = nib.load(GLM3_path_decision + 'group/unthresholded_decision_long_pm_zscore.nii.gz')
GLM3_unthreshold_decision_short = nib.load(GLM3_path_decision + 'group/unthresholded_decision_short_pm_zscore.nii.gz')

GLM3_decision_long_raw_mask, GLM3_decision_long_threshold = threshold_stats_img(
    GLM3_unthreshold_decision_long, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

GLM3_decision_short_raw_mask, GLM3_decision_short_threshold = threshold_stats_img(
    GLM3_unthreshold_decision_short, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

# making integrated mask, peak voxel + valuation
GLM3_decision_long_raw_mask_data = GLM3_decision_long_raw_mask.get_fdata()
GLM3_decision_long_raw_mask_ = (GLM3_decision_long_raw_mask_data > GLM3_decision_long_threshold).astype(np.uint8)
GLM3_decision_long_len = len(GLM3_decision_long_raw_mask_[GLM3_decision_long_raw_mask_==1]) # number of surviving voxel
GLM3_decision_long_mask = nib.Nifti1Image(GLM3_decision_long_raw_mask_, 
                                           affine=GLM3_unthreshold_decision_long.affine, 
                                           header=GLM3_unthreshold_decision_long.header)

GLM3_decision_short_raw_mask_data = GLM3_decision_short_raw_mask.get_fdata()
GLM3_decision_short_raw_mask_ = (GLM3_decision_short_raw_mask_data > GLM3_decision_short_threshold).astype(np.uint8)
GLM3_decision_short_len = len(GLM3_decision_short_raw_mask_[GLM3_decision_short_raw_mask_==1]) # number of surviving voxel
GLM3_decision_short_mask = nib.Nifti1Image(GLM3_decision_short_raw_mask_, 
                                           affine=GLM3_unthreshold_decision_short.affine, 
                                           header=GLM3_unthreshold_decision_short.header)

GLM3_decision_long_masker = NiftiMasker(mask_img = GLM3_decision_long_mask)
GLM3_decision_short_masker = NiftiMasker(mask_img = GLM3_decision_short_mask)

subjlist = [x for x, _, _ in os.walk(GLM3_path_decision) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM3_decision_long_pe = np.empty((nsub, GLM3_decision_long_len))
GLM3_decision_short_pe = np.empty((nsub, GLM3_decision_short_len))
GLM3_decision_long_close = np.empty((len(close_group), GLM3_decision_long_len))
GLM3_decision_short_close = np.empty((len(close_group), GLM3_decision_short_len))
GLM3_decision_long_far = np.empty((len(far_group), GLM3_decision_long_len))
GLM3_decision_short_far = np.empty((len(far_group), GLM3_decision_short_len))
close_index = 0
far_index = 0

for s in range(nsub):
    subjpath = subjlist[s]
    GLM3_decision_long = nib.load(subjpath + '/decision_long_pm_beta_smoothed.nii.gz')
    GLM3_decision_short = nib.load(subjpath + '/decision_short_pm_beta_smoothed.nii.gz')
    
    GLM3_decision_long_masked = GLM3_decision_long_masker.fit_transform(GLM3_decision_long).squeeze()
    GLM3_decision_short_masked = GLM3_decision_short_masker.fit_transform(GLM3_decision_short).squeeze()
    
    GLM3_decision_long_pe[s,:] =  GLM3_decision_long_masked
    GLM3_decision_short_pe[s,:] =  GLM3_decision_short_masked
    
    if subjpath[-7:] in close_group:
        GLM3_decision_long_close[close_index,:] = GLM3_decision_long_masked
        GLM3_decision_short_close[close_index,:] = GLM3_decision_short_masked
        close_index += 1
    elif subjpath[-7:] in far_group:
        GLM3_decision_long_far[far_index,:] = GLM3_decision_long_masked
        GLM3_decision_short_far[far_index,:] = GLM3_decision_short_masked
        far_index += 1
         
GLM3_decision_long_mean = GLM3_decision_long_pe.mean(axis=(0))
GLM3_decision_short_mean = GLM3_decision_short_pe.mean(axis=(0))
GLM3_decision_long_close_mean = GLM3_decision_long_close.mean(axis=(0))
GLM3_decision_short_close_mean = GLM3_decision_short_close.mean(axis=(0))
GLM3_decision_long_far_mean = GLM3_decision_long_far.mean(axis=(0))
GLM3_decision_short_far_mean = GLM3_decision_short_far.mean(axis=(0))

GLM3_decision_long_t_test = ttest_1samp(GLM3_decision_long_mean, 0)
GLM3_decision_short_t_test = ttest_1samp(GLM3_decision_short_mean, 0)
GLM3_decision_long_far_close_t_test = ttest_ind(GLM3_decision_long_close_mean,
                                                GLM3_decision_long_far_mean)
GLM3_decision_short_far_close_t_test = ttest_ind(GLM3_decision_short_close_mean,
                                                 GLM3_decision_short_far_mean)

    
# GLM3, confirmation
GLM3_path_confirmation = 'GLM3_results_confirmation/' # decision, matrix generated in a nilearn manner

# selecting peak voxels
GLM3_unthreshold_confirmation_long = nib.load(GLM3_path_confirmation + 'group/unthresholded_confirmation_long_pm_zscore.nii.gz')
GLM3_unthreshold_confirmation_short = nib.load(GLM3_path_confirmation + 'group/unthresholded_confirmation_short_pm_zscore.nii.gz')

GLM3_confirmation_long_raw_mask, GLM3_confirmation_long_threshold = threshold_stats_img(
    GLM3_unthreshold_confirmation_long, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

GLM3_confirmation_short_raw_mask, GLM3_confirmation_short_threshold = threshold_stats_img(
    GLM3_unthreshold_confirmation_short, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

# making integrated mask, peak voxel + valuation
GLM3_confirmation_long_raw_mask_data = GLM3_confirmation_long_raw_mask.get_fdata()
GLM3_confirmation_long_raw_mask_ = (GLM3_confirmation_long_raw_mask_data > GLM3_confirmation_long_threshold).astype(np.uint8)
GLM3_confirmation_long_len = len(GLM3_confirmation_long_raw_mask_[GLM3_confirmation_long_raw_mask_==1]) # number of surviving voxel
GLM3_confirmation_long_mask = nib.Nifti1Image(GLM3_confirmation_long_raw_mask_, 
                                           affine=GLM3_unthreshold_confirmation_long.affine, 
                                           header=GLM3_unthreshold_confirmation_long.header)

GLM3_confirmation_short_raw_mask_data = GLM3_confirmation_short_raw_mask.get_fdata()
GLM3_confirmation_short_raw_mask_ = (GLM3_confirmation_short_raw_mask_data > GLM3_confirmation_short_threshold).astype(np.uint8)
GLM3_confirmation_short_len = len(GLM3_confirmation_long_raw_mask_[GLM3_confirmation_long_raw_mask_==1]) # number of surviving voxel
GLM3_confirmation_short_mask = nib.Nifti1Image(GLM3_confirmation_short_raw_mask_, 
                                           affine=GLM3_unthreshold_confirmation_short.affine, 
                                           header=GLM3_unthreshold_confirmation_short.header)

GLM3_confirmation_long_masker = NiftiMasker(mask_img = GLM3_confirmation_long_mask)
GLM3_confirmation_short_masker = NiftiMasker(mask_img = GLM3_confirmation_short_mask)

subjlist = [x for x, _, _ in os.walk(GLM3_path_confirmation) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM3_confirmation_long_pe = np.empty((nsub, GLM3_confirmation_long_len))
GLM3_confirmation_short_pe = np.empty((nsub, GLM3_confirmation_short_len))
GLM3_confirmation_long_close = np.empty((len(close_group), GLM3_confirmation_long_len))
GLM3_confirmation_short_close = np.empty((len(close_group), GLM3_confirmation_short_len))
GLM3_confirmation_long_far = np.empty((len(far_group), GLM3_confirmation_long_len))
GLM3_confirmation_short_far = np.empty((len(far_group), GLM3_confirmation_short_len))
close_index = 0
far_index = 0

# for s in range(nsub):
#     subjpath = subjlist[s]
#     # GLM3_confirmation_long = nib.load(subjpath + '/confirmation_long_pm_beta_smoothed.nii.gz')
#     GLM3_confirmation_short = nib.load(subjpath + '/confirmation_short_pm_beta_smoothed.nii.gz')
    
#     # GLM3_confirmation_long_masked = GLM3_confirmation_long_masker.fit_transform(GLM3_confirmation_long).squeeze()
#     GLM3_confirmation_short_masked = GLM3_confirmation_short_masker.fit_transform(GLM3_confirmation_short).squeeze()
    
#     # GLM3_confirmation_long_pe[s,:] =  GLM3_confirmation_long_masked
#     GLM3_confirmation_short_pe[s,:] =  GLM3_confirmation_short_masked
    
#     if subjpath[-7:] in close_group:
#         # GLM3_confirmation_long_close[close_index,:] = GLM3_confirmation_long_masked
#         GLM3_confirmation_short_close[close_index,:] = GLM3_confirmation_short_masked
#         close_index += 1
#     elif subjpath[-7:] in far_group:
#         # GLM3_confirmation_long_far[far_index,:] = GLM3_confirmation_long_masked
#         GLM3_confirmation_short_far[far_index,:] = GLM3_confirmation_short_masked
#         far_index += 1
    
# # GLM3_confirmation_long_mean = GLM3_confirmation_long_pe.mean(axis=(0))
# GLM3_confirmation_short_mean = GLM3_confirmation_short_pe.mean(axis=(0))
# # GLM3_confirmation_long_close_mean = GLM3_confirmation_long_close.mean(axis=(0))
# GLM3_confirmation_short_close_mean = GLM3_confirmation_short_close.mean(axis=(0))
# # GLM3_confirmation_long_far_mean = GLM3_confirmation_long_far.mean(axis=(0))
# GLM3_confirmation_short_far_mean = GLM3_confirmation_short_far.mean(axis=(0))

# # GLM3_confirmation_long_t_test = ttest_1samp(GLM3_confirmation_long_mean, 0)
# GLM3_confirmation_short_t_test = ttest_1samp(GLM3_confirmation_short_mean, 0) 
# # GLM3_confirmation_long_far_close_t_test = ttest_ind(GLM3_confirmation_long_close_mean,
# #                                                     GLM3_confirmation_long_far_mean)
# GLM3_confirmation_short_far_close_t_test = ttest_ind(GLM3_confirmation_short_close_mean,
#                                                      GLM3_confirmation_short_far_mean)

# GLM4, decision
GLM4_path_decision = 'GLM4_results_nilearn/' # decision, matrix generated in a nilearn manner

# selecting peak voxels
GLM4_unthreshold_decision_long = nib.load(GLM4_path_decision + 'group/unthresholded_decision_long_pm_zscore.nii.gz')
GLM4_unthreshold_decision_short = nib.load(GLM4_path_decision + 'group/unthresholded_decision_short_pm_zscore.nii.gz')

GLM4_decision_long_raw_mask, GLM4_decision_long_threshold = threshold_stats_img(
    GLM4_unthreshold_decision_long, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

GLM4_decision_short_raw_mask, GLM4_decision_short_threshold = threshold_stats_img(
    GLM4_unthreshold_decision_short, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

# making integrated mask, peak voxel + valuation
GLM4_decision_long_raw_mask_data = GLM4_decision_long_raw_mask.get_fdata()
GLM4_decision_long_raw_mask_ = (GLM4_decision_long_raw_mask_data > GLM4_decision_long_threshold).astype(np.uint8)
GLM4_decision_long_len = len(GLM4_decision_long_raw_mask_[GLM4_decision_long_raw_mask_==1]) # number of surviving voxel
GLM4_decision_long_mask = nib.Nifti1Image(GLM4_decision_long_raw_mask_, 
                                           affine=GLM4_unthreshold_decision_long.affine, 
                                           header=GLM4_unthreshold_decision_long.header)

GLM4_decision_short_raw_mask_data = GLM4_decision_short_raw_mask.get_fdata()
GLM4_decision_short_raw_mask_ = (GLM4_decision_short_raw_mask_data > GLM4_decision_short_threshold).astype(np.uint8)
GLM4_decision_short_len = len(GLM4_decision_short_raw_mask_[GLM4_decision_short_raw_mask_==1]) # number of surviving voxel
GLM4_decision_short_mask = nib.Nifti1Image(GLM4_decision_short_raw_mask_, 
                                           affine=GLM4_unthreshold_decision_short.affine, 
                                           header=GLM4_unthreshold_decision_short.header)

GLM4_decision_long_masker = NiftiMasker(mask_img = GLM4_decision_long_mask)
GLM4_decision_short_masker = NiftiMasker(mask_img = GLM4_decision_short_mask)

subjlist = [x for x, _, _ in os.walk(GLM4_path_decision) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM4_decision_long_pe = np.empty((nsub, GLM4_decision_long_len))
GLM4_decision_short_pe = np.empty((nsub, GLM4_decision_short_len))
GLM4_decision_long_close = np.empty((len(close_group), GLM4_decision_long_len))
GLM4_decision_short_close = np.empty((len(close_group), GLM4_decision_short_len))
GLM4_decision_long_far = np.empty((len(far_group), GLM4_decision_long_len))
GLM4_decision_short_far = np.empty((len(far_group), GLM4_decision_short_len))
close_index = 0
far_index = 0

for s in range(nsub):
    subjpath = subjlist[s]
    GLM4_decision_long = nib.load(subjpath + '/decision_long_pm_beta_smoothed.nii.gz')
    GLM4_decision_short = nib.load(subjpath + '/decision_short_pm_beta_smoothed.nii.gz')
    
    GLM4_decision_long_masked = GLM4_decision_long_masker.fit_transform(GLM4_decision_long).squeeze()
    GLM4_decision_short_masked = GLM4_decision_short_masker.fit_transform(GLM4_decision_short).squeeze()
    
    GLM4_decision_long_pe[s,:] =  GLM4_decision_long_masked
    GLM4_decision_short_pe[s,:] =  GLM4_decision_short_masked
    
    if subjpath[-7:] in close_group:
        GLM4_decision_long_close[close_index,:] = GLM4_decision_long_masked
        GLM4_decision_short_close[close_index,:] = GLM4_decision_short_masked
        close_index += 1
    elif subjpath[-7:] in far_group:
        GLM4_decision_long_far[far_index,:] = GLM4_decision_long_masked
        GLM4_decision_short_far[far_index,:] = GLM4_decision_short_masked
        far_index += 1
         
GLM4_decision_long_mean = GLM4_decision_long_pe.mean(axis=(0))
GLM4_decision_short_mean = GLM4_decision_short_pe.mean(axis=(0))
GLM4_decision_long_close_mean = GLM4_decision_long_close.mean(axis=(0))
GLM4_decision_short_close_mean = GLM4_decision_short_close.mean(axis=(0))
GLM4_decision_long_far_mean = GLM4_decision_long_far.mean(axis=(0))
GLM4_decision_short_far_mean = GLM4_decision_short_far.mean(axis=(0))

GLM4_decision_long_t_test = ttest_1samp(GLM4_decision_long_mean, 0)
GLM4_decision_short_t_test = ttest_1samp(GLM4_decision_short_mean, 0)
GLM4_decision_long_far_close_t_test = ttest_ind(GLM4_decision_long_close_mean,
                                                GLM4_decision_long_far_mean)
GLM4_decision_short_far_close_t_test = ttest_ind(GLM4_decision_short_close_mean,
                                                 GLM4_decision_short_far_mean)

    
# GLM4, confirmation
GLM4_path_confirmation = 'GLM4_results_confirmation/' # decision, matrix generated in a nilearn manner

# selecting peak voxels
GLM4_unthreshold_confirmation_long = nib.load(GLM4_path_confirmation + 'group/unthresholded_confirmation_long_pm_zscore.nii.gz')
GLM4_unthreshold_confirmation_short = nib.load(GLM4_path_confirmation + 'group/unthresholded_confirmation_short_pm_zscore.nii.gz')

GLM4_confirmation_long_raw_mask, GLM4_confirmation_long_threshold = threshold_stats_img(
    GLM4_unthreshold_confirmation_long, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

GLM4_confirmation_short_raw_mask, GLM4_confirmation_short_threshold = threshold_stats_img(
    GLM4_unthreshold_confirmation_short, mask_img = mask,
    alpha=0.05, height_control="fdr", # equal to abs(z) > 2.37
    cluster_threshold=0
)

# making integrated mask, peak voxel + valuation
GLM4_confirmation_long_raw_mask_data = GLM4_confirmation_long_raw_mask.get_fdata()
GLM4_confirmation_long_raw_mask_ = (GLM4_confirmation_long_raw_mask_data > GLM4_confirmation_long_threshold).astype(np.uint8)
GLM4_confirmation_long_len = len(GLM4_confirmation_long_raw_mask_[GLM4_confirmation_long_raw_mask_==1]) # number of surviving voxel
GLM4_confirmation_long_mask = nib.Nifti1Image(GLM4_confirmation_long_raw_mask_, 
                                           affine=GLM4_unthreshold_confirmation_long.affine, 
                                           header=GLM4_unthreshold_confirmation_long.header)

GLM4_confirmation_short_raw_mask_data = GLM4_confirmation_short_raw_mask.get_fdata()
GLM4_confirmation_short_raw_mask_ = (GLM4_confirmation_short_raw_mask_data > GLM4_confirmation_short_threshold).astype(np.uint8)
GLM4_confirmation_short_len = len(GLM4_confirmation_short_raw_mask_[GLM4_confirmation_short_raw_mask_==1]) # number of surviving voxel
GLM4_confirmation_short_mask = nib.Nifti1Image(GLM4_confirmation_short_raw_mask_, 
                                           affine=GLM4_unthreshold_confirmation_short.affine, 
                                           header=GLM4_unthreshold_confirmation_short.header)

GLM4_confirmation_long_masker = NiftiMasker(mask_img = GLM4_confirmation_long_mask)
GLM4_confirmation_short_masker = NiftiMasker(mask_img = GLM4_confirmation_short_mask)


subjlist = [x for x, _, _ in os.walk(GLM4_path_confirmation) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM4_confirmation_long_pe = np.empty((nsub, GLM4_confirmation_long_len))
GLM4_confirmation_short_pe = np.empty((nsub, GLM4_confirmation_short_len))
GLM4_confirmation_long_close = np.empty((len(close_group), GLM4_confirmation_long_len))
GLM4_confirmation_short_close = np.empty((len(close_group), GLM4_confirmation_short_len))
GLM4_confirmation_long_far = np.empty((len(far_group), GLM4_confirmation_long_len))
GLM4_confirmation_short_far = np.empty((len(far_group), GLM4_confirmation_short_len))
close_index = 0
far_index = 0

for s in range(nsub):
    subjpath = subjlist[s]
    GLM4_confirmation_long = nib.load(subjpath + '/confirmation_long_pm_beta_smoothed.nii.gz')
    GLM4_confirmation_short = nib.load(subjpath + '/confirmation_short_pm_beta_smoothed.nii.gz')
    
    GLM4_confirmation_long_masked = GLM4_confirmation_long_masker.fit_transform(GLM4_confirmation_long).squeeze()
    GLM4_confirmation_short_masked = GLM4_confirmation_short_masker.fit_transform(GLM4_confirmation_short).squeeze()
    
    GLM4_confirmation_long_pe[s,:] =  GLM4_confirmation_long_masked
    GLM4_confirmation_short_pe[s,:] =  GLM4_confirmation_short_masked
    
    if subjpath[-7:] in close_group:
        GLM4_confirmation_long_close[close_index,:] = GLM4_confirmation_long_masked
        GLM4_confirmation_short_close[close_index,:] = GLM4_confirmation_short_masked
        close_index += 1
    elif subjpath[-7:] in far_group:
        GLM4_confirmation_long_far[far_index,:] = GLM4_confirmation_long_masked
        GLM4_confirmation_short_far[far_index,:] = GLM4_confirmation_short_masked
        far_index += 1
    
GLM4_confirmation_long_mean = GLM4_confirmation_long_pe.mean(axis=(0))
GLM4_confirmation_short_mean = GLM4_confirmation_short_pe.mean(axis=(0))
GLM4_confirmation_long_close_mean = GLM4_confirmation_long_close.mean(axis=(0))
GLM4_confirmation_short_close_mean = GLM4_confirmation_short_close.mean(axis=(0))
GLM4_confirmation_long_far_mean = GLM4_confirmation_long_far.mean(axis=(0))
GLM4_confirmation_short_far_mean = GLM4_confirmation_short_far.mean(axis=(0))

GLM4_confirmation_long_t_test = ttest_1samp(GLM4_confirmation_long_mean, 0)
GLM4_confirmation_short_t_test = ttest_1samp(GLM4_confirmation_short_mean, 0) 
GLM4_confirmation_long_far_close_t_test = ttest_ind(GLM4_confirmation_long_close_mean,
                                                    GLM4_confirmation_long_far_mean)
GLM4_confirmation_short_far_close_t_test = ttest_ind(GLM4_confirmation_short_close_mean,
                                                     GLM4_confirmation_short_far_mean)

# individual difference



