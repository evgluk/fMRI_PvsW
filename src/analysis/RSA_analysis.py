#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# codes for RSA of overlapping brain regions involved in delay discounting
# =============================================================================
import os
import numpy as np
from nilearn.image import new_img_like
import nibabel as nib
from nilearn.glm.thresholding import threshold_stats_img
from nilearn.reporting import get_clusters_table
from scipy import stats
from numpy import inf

# load subject data
def load_data():
    path = 'GLM1_results/'
    subjlist = [x for x, _, _ in os.walk(path) if 'sub' in x and os.path.isdir(x)]
    subjlist.sort()
    nsub = len(subjlist)
    
    subjbetas = np.empty((len(subjlist),4, 53, 65, 45))
    subjbetas[:] = np.nan

    for s in range(nsub):
        subjpath = subjlist[s]
        pe1 = nib.load(subjpath + '/decision_long_beta_unsmoothed.nii.gz')
        pe2 = nib.load(subjpath + '/decision_short_beta_unsmoothed.nii.gz')
        pe3 = nib.load(subjpath + '/confirmation_long_beta_unsmoothed.nii.gz')
        pe4 = nib.load(subjpath + '/confirmation_short_beta_unsmoothed.nii.gz')
        
        subjbetas[s,0,:] = np.squeeze(pe1.get_fdata())
        subjbetas[s,1,:] = np.squeeze(pe2.get_fdata())
        subjbetas[s,2,:] = np.squeeze(pe3.get_fdata())
        subjbetas[s,3,:] = np.squeeze(pe4.get_fdata())
    
    return subjbetas, nsub

def RSA_statistics(num_permutation):
    print('running statistic interfrence...')
    # only run tests in voxels with a group average beta > 0
    subjbetas, nsub = load_data()
    avgsubjbetas = np.nanmean(subjbetas, axis = (0,1))
    mask = np.full((53,65,45), False)
    mask[avgsubjbetas != 0] = True
    centers = list(zip(*np.nonzero(mask)))
    
    # loading subject rsa
    sub_rsa = np.empty((nsub,53,65,45))
    sub_rsa[:] = np.nan
    permutation_rsa = np.empty((nsub,num_permutation,53,65,45))
    permutation_rsa[:] = np.nan
    for s in range(nsub):
        sub_data = np.load('RSA_results/subject_RSA/sub{}_RSA_result.npy'.format(s))
        permutation_data = np.load('subject_RSA_permutation/sub{}_RSA_result_permutation.npy'.format(s))
        sub_rsa[s,:] = sub_data
        permutation_rsa[s,:] = permutation_data
    
    mean_sub_rsa = np.nanmean(sub_rsa, axis = 0)
    mean_permutation_rsa = np.nanmean(permutation_rsa, axis = 0)
    
    np.save('RSA_results/mean_subject_rsa.npy', mean_sub_rsa)
    np.save('RSA_results/mean_permutation_rsa.npy', mean_permutation_rsa)
    
    zmap = np.empty((53,65,45))
    zmap[:] = np.nan
    
    pmap = np.empty((53,65,45))
    pmap[:] = np.nan
    
    # loop over all voxels
    for c in centers:
        value = mean_sub_rsa[c[0], c[1], c[2]]
        permutation_value = mean_permutation_rsa[:, c[0], c[1], c[2]]
        
        p = len(permutation_value[permutation_value > value])/num_permutation
        pmap[c[0], c[1], c[2]] = p
        zmap[c[0], c[1], c[2]] = stats.norm.ppf(1 - p/2) # one-tail hypothesis testing
        
    # all nans are replaced by zeros.
    zmap[np.isnan(zmap)] = 0
    zmap[zmap == inf] = 0
    
    np.save('RSA_results/pmap.npy', pmap)
    np.save('RSA_results/zmap.npy', zmap)
    
    # convert the np array of z values to a nifti image
    ref_img = nib.load('GLM1_results/sub-001/decision_long_beta_unsmoothed.nii.gz')
    zmap_img = new_img_like(ref_img, zmap)
            
    # multiple comparison correction and cluster thresholding
    thresholded_zmap, threshold = threshold_stats_img(zmap_img, alpha = .05, height_control = 'fdr', 
                                                cluster_threshold = 30) 
    
    thresholded_zmap.to_filename('RSA_results/thresholded_rsa_overlapping.nii.gz') 
    cluster_table = get_clusters_table(thresholded_zmap, threshold, cluster_threshold=30)
    cluster_table.to_csv('RSA_results/thresholded_rsa_overlapping_cluster.csv')
 
if __name__ == '__main__':
    RSA_statistics(1000)
