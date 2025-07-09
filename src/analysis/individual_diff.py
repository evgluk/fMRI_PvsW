#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# codes for individual difference
# =============================================================================
import nibabel as nib
from nilearn.maskers import NiftiMasker
from nilearn.image import resample_to_img
import os
import pandas as pd
import scipy.stats as st
import numpy as np 
import matplotlib.pyplot as plt

# Resample the ROI mask to match the functional image
func = nib.load('imgdata/sub-001/func/sub-001_task-delay_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
raw_mask = nib.load('Bartra3A_and_Clithero3_meta_mask.nii')
mask = resample_to_img(raw_mask, func, interpolation='nearest')
masker = NiftiMasker(mask_img = mask)

# load logks
logks = pd.read_csv('behavior_data/fMRI_fits.csv')

# set figure font
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.style'] = 'normal'

# GLM2, decision
GLM2_path_decision = 'GLM2_results_nilearn/' # decision, matrix generated in a nilearn manner

subjlist = [x for x, _, _ in os.walk(GLM2_path_decision) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM2_decision_long_pe = np.empty((nsub, 504)) 
GLM2_decision_short_pe = np.empty((nsub, 504))
GLM2_decision_long_logk = np.empty((nsub, 1)) 
GLM2_decision_short_logk = np.empty((nsub, 1))

for s in range(nsub):
    subjpath = subjlist[s]
    GLM2_decision_long = nib.load(subjpath + '/decision_long_pm_beta_smoothed.nii.gz')
    GLM2_decision_short = nib.load(subjpath + '/decision_short_pm_beta_smoothed.nii.gz')
    
    GLM2_decision_long_masked = masker.fit_transform(GLM2_decision_long).squeeze()
    GLM2_decision_short_masked = masker.fit_transform(GLM2_decision_short).squeeze()
    
    GLM2_decision_long_pe[s,:] =  GLM2_decision_long_masked
    GLM2_decision_short_pe[s,:] =  GLM2_decision_short_masked
    GLM2_decision_long_logk[s,:] = logks[logks['BIDS_ID'] == subjpath[-7:]]['K_L'].item()
    GLM2_decision_short_logk[s,:] = logks[logks['BIDS_ID'] == subjpath[-7:]]['K_S'].item()

GLM2_decision_long_pe = GLM2_decision_long_pe.mean(axis = 1)
GLM2_decision_short_pe = GLM2_decision_short_pe.mean(axis = 1)
GLM2_decision_long_logk = GLM2_decision_long_logk.squeeze()
GLM2_decision_short_logk = GLM2_decision_short_logk.squeeze()
GLM2_decision_absdiff_pe = abs(np.subtract(GLM2_decision_long_pe, GLM2_decision_short_pe))
GLM2_decision_absdiff_logk = abs(np.subtract(GLM2_decision_long_logk, GLM2_decision_short_logk))
 
GLM2_long_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM2_decision_long_logk, GLM2_decision_long_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM2_decision_long_logk, GLM2_decision_long_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM2_decision_long_logk, intercept + slope * GLM2_decision_long_logk, label=line, color = '#203972')
plt.title("Magnitude sensitivity, long tasks", size = 18)
plt.xlabel('log($K_L$)', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Magnitude beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)    

GLM2_short_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM2_decision_short_logk, GLM2_decision_short_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM2_decision_short_logk, GLM2_decision_short_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM2_decision_short_logk, intercept + slope * GLM2_decision_short_logk, label=line, color = '#203972')
plt.title("Magnitude sensitivity, short tasks", size = 18)
plt.xlabel('log($K_S$)', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Magnitude beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)  
     
GLM2_absdiff_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM2_decision_absdiff_logk, GLM2_decision_absdiff_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM2_decision_absdiff_logk, GLM2_decision_absdiff_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM2_decision_absdiff_logk, intercept + slope * GLM2_decision_absdiff_logk, label=line, color = '#203972')
plt.title("Magnitude sensitivity, abstract difference", size = 18)
plt.xlabel('|$logK_L$ -  $logK_S$|', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Magnitude beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)  

# GLM3, decision
GLM3_path_decision = 'GLM3_results_nilearn/' # decision, matrix generated in a nilearn manner

subjlist = [x for x, _, _ in os.walk(GLM3_path_decision) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM3_decision_long_pe = np.empty((nsub, 504)) 
GLM3_decision_short_pe = np.empty((nsub, 504))
GLM3_decision_long_logk = np.empty((nsub, 1)) 
GLM3_decision_short_logk = np.empty((nsub, 1))

for s in range(nsub):
    subjpath = subjlist[s]
    GLM3_decision_long = nib.load(subjpath + '/decision_long_pm_beta_smoothed.nii.gz')
    GLM3_decision_short = nib.load(subjpath + '/decision_short_pm_beta_smoothed.nii.gz')
    
    GLM3_decision_long_masked = masker.fit_transform(GLM3_decision_long).squeeze()
    GLM3_decision_short_masked = masker.fit_transform(GLM3_decision_short).squeeze()
    
    GLM3_decision_long_pe[s,:] =  GLM3_decision_long_masked
    GLM3_decision_short_pe[s,:] =  GLM3_decision_short_masked
    GLM3_decision_long_logk[s,:] = logks[logks['BIDS_ID'] == subjpath[-7:]]['K_L']
    GLM3_decision_short_logk[s,:] = logks[logks['BIDS_ID'] == subjpath[-7:]]['K_S']

GLM3_decision_long_pe = GLM3_decision_long_pe.mean(axis = 1)
GLM3_decision_short_pe = GLM3_decision_short_pe.mean(axis = 1)
GLM3_decision_long_logk = GLM3_decision_long_logk.squeeze()
GLM3_decision_short_logk = GLM3_decision_short_logk.squeeze()
GLM3_decision_absdiff_pe = abs(np.subtract(GLM3_decision_long_pe, GLM3_decision_short_pe))
GLM3_decision_absdiff_logk = abs(np.subtract(GLM3_decision_long_logk, GLM3_decision_short_logk))
   
GLM3_long_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM3_decision_long_logk, GLM3_decision_long_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM3_decision_long_logk, GLM3_decision_long_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM3_decision_long_logk, intercept + slope * GLM3_decision_long_logk, label=line, color = '#203972')
plt.title("Delay sensitivity, long tasks", size = 18)
plt.xlabel('log($K_L$)', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Delay beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)    

GLM3_short_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM3_decision_short_logk, GLM3_decision_short_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM3_decision_short_logk, GLM3_decision_short_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM3_decision_short_logk, intercept + slope * GLM3_decision_short_logk, label=line, color = '#203972')
plt.title("Delay sensitivity, short tasks", size = 18)
plt.xlabel('log($K_S$)', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Delay beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)  
     
GLM3_absdiff_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM3_decision_absdiff_logk, GLM3_decision_absdiff_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM3_decision_absdiff_logk, GLM3_decision_absdiff_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM3_decision_absdiff_logk, intercept + slope * GLM3_decision_absdiff_logk, label=line, color = '#203972')
plt.title("Delay sensitivity, abstract difference", size = 18)
plt.xlabel('|$logK_L$ -  $logK_S$|', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Delay beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)  
   
# GLM4, decision
GLM4_path_decision = 'GLM4_results_nilearn/' # decision, matrix generated in a nilearn manner

subjlist = [x for x, _, _ in os.walk(GLM4_path_decision) if 'sub' in x and os.path.isdir(x)]
subjlist.sort()
nsub = len(subjlist)
GLM4_decision_long_pe = np.empty((nsub, 504)) 
GLM4_decision_short_pe = np.empty((nsub, 504))
GLM4_decision_long_logk = np.empty((nsub, 1)) 
GLM4_decision_short_logk = np.empty((nsub, 1))

for s in range(nsub):
    subjpath = subjlist[s]
    GLM4_decision_long = nib.load(subjpath + '/decision_long_pm_beta_smoothed.nii.gz')
    GLM4_decision_short = nib.load(subjpath + '/decision_short_pm_beta_smoothed.nii.gz')
    
    GLM4_decision_long_masked = masker.fit_transform(GLM4_decision_long).squeeze()
    GLM4_decision_short_masked = masker.fit_transform(GLM4_decision_short).squeeze()
    
    GLM4_decision_long_pe[s,:] =  GLM4_decision_long_masked
    GLM4_decision_short_pe[s,:] =  GLM4_decision_short_masked
    GLM4_decision_long_logk[s,:] = logks[logks['BIDS_ID'] == subjpath[-7:]]['K_L']
    GLM4_decision_short_logk[s,:] = logks[logks['BIDS_ID'] == subjpath[-7:]]['K_S']
    
GLM4_decision_long_pe = GLM4_decision_long_pe.mean(axis = 1)
GLM4_decision_short_pe = GLM4_decision_short_pe.mean(axis = 1)
GLM4_decision_long_logk = GLM4_decision_long_logk.squeeze()
GLM4_decision_short_logk = GLM4_decision_short_logk.squeeze()
GLM4_decision_absdiff_pe = abs(np.subtract(GLM4_decision_long_pe, GLM4_decision_short_pe))
GLM4_decision_absdiff_logk = abs(np.subtract(GLM4_decision_long_logk, GLM4_decision_short_logk))
   
GLM4_long_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM4_decision_long_logk, GLM4_decision_long_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM4_decision_long_logk, GLM4_decision_long_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM4_decision_long_logk, intercept + slope * GLM4_decision_long_logk, label=line, color = '#203972')
plt.title("Subjective value sensitivity, long tasks", size = 18)
plt.xlabel('log($K_L$)', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Subjective value beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)    

GLM4_short_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM4_decision_short_logk, GLM4_decision_short_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM4_decision_short_logk, GLM4_decision_short_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM4_decision_short_logk, intercept + slope * GLM4_decision_short_logk, label=line, color = '#203972')
plt.title("Subjective value sensitivity, short tasks", size = 18)
plt.xlabel('log($K_S$)', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Subjective value beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)  
     
GLM4_absdiff_logk_corr = plt.figure(figsize=(6,6))
slope, intercept, r, p, stderr = st.linregress(GLM4_decision_absdiff_logk, GLM4_decision_absdiff_pe)
line = f'r = {r:.2f}, p = {p:.2f}'
plt.plot(GLM4_decision_absdiff_logk, GLM4_decision_absdiff_pe, linewidth=0, marker='8', color = '#CCAED4', alpha = 0.8)
plt.plot(GLM4_decision_absdiff_logk, intercept + slope * GLM4_decision_absdiff_logk, label=line, color = '#203972')
plt.title("Subjective value sensitivity, abstract difference", size = 18)
plt.xlabel('|$logK_L$ -  $logK_S$|', size = 18)
plt.xticks(fontsize=18)
plt.ylabel('Subjective value beta values', size = 18)
plt.yticks(fontsize=18)
plt.legend(facecolor='white', fontsize=12, loc = 2)  
   