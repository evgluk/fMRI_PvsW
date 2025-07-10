#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================================
# codes for RSA permutation anlaysis of overlapping brain regions involved in delay discounting
# =============================================================================================
import os
import numpy as np
from nilearn.image import new_img_like
import nibabel as nib
from nilearn.glm.thresholding import threshold_stats_img
from nilearn.reporting import get_clusters_table
from scipy import stats
from numpy import inf
from rsatoolbox.inference import eval_fixed
from rsatoolbox.model import ModelFixed
from rsatoolbox.util.searchlight import get_volume_searchlight, get_searchlight_RDMs, evaluate_models_searchlight
from rsatoolbox.rdm.rdms import permute_rdms

# returns the upper triangle
def upper_tri(RDM):
    m = RDM.shape[0]
    r, c = np.triu_indices(m, 1)
    return RDM[r, c]

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

def run_RSA(num_permutation):
    
    # create model RDMs
    # 0 -- perfect correlation
    # 1 -- no correlation 
    # 2 -- perfect anti-correlation
    H1_rawRDM = np.array([[0,0,1,1],
                          [0,0,1,1],
                          [1,1,0,1],
                          [1,1,1,0]])
    
    H1_RDM = ModelFixed('H1 RDM', upper_tri(H1_rawRDM))
    
    # load subject betas
    subjbetas, nsub = load_data()
    
    for s in range(nsub):
        print('RSA is running')
        print('this is {}th subject'.format(s))
        subjbeta = subjbetas[s,]
        
        outputs = np.empty((53,65,45))
        outputs[:] = np.nan
        
        # I generate a whole-brain mask by only selecting voxels with valid signals 
        # (non-zero) based on avearage beta values across conditions per subject
        avgsubjbetas = np.nanmean(subjbeta, axis = 0)
        mask = np.full((53,65,45), False)
        mask[avgsubjbetas != 0] = True

        # To select neighbors that are 1 voxel away, one needs to specify a radius of 2.
        # the threshold describes the proportion of voxels would be accepted to be
        # out side of brain mask
        centers, neighbors = get_volume_searchlight(mask, radius=2, threshold=0.5)
        conditions = np.arange(4)
        
        # create subject neural RDM
        subjbetas_2d = subjbeta.reshape([subjbeta.shape[0], -1])
        subjRDM = get_searchlight_RDMs(subjbetas_2d, centers, neighbors, conditions, method='correlation')
        # subjRDM.dissimilarities = 1 - np.array(subjRDM.dissimilarities)
        
        # do the computation
        # scores range from -1 (opposite) to 0 (orthogonal) to 1 (similar)
        eval_results = evaluate_models_searchlight(subjRDM, H1_RDM, eval_fixed, method='cosine_cov')
        eval_score = [float(e.evaluations) for e in eval_results]
        # eval_score_norm = stats.mstats.zscore(eval_score, nan_policy = 'omit')
        
        # convert RSA results into the brain size
        subjRDM_brain = np.empty([53*65*45])
        subjRDM_brain[:] = np.nan
        subjRDM_brain[list(subjRDM.rdm_descriptors['voxel_index'])] = eval_score
        subjRDM_brain = subjRDM_brain.reshape([53, 65, 45])
        outputs[:] = subjRDM_brain
        
        np.save('RSA_result/subject_RSA/sub{}_RSA_result.npy'.format(s), outputs)
        
        permuted_rslt = np.empty((num_permutation,53,65,45))
        permuted_rslt[:] = np.nan
        
        for i in range(num_permutation):
            print('this is {} iter for subject {}'.format(i, s))
            permuted_subjRDM = permute_rdms(subjRDM)
            permuted_eval_results = evaluate_models_searchlight(permuted_subjRDM, H1_RDM, eval_fixed, method='cosine_cov')
            permuted_eval_score = [float(e.evaluations) for e in permuted_eval_results]
            
            permuted_subjRDM_brain = np.empty([53*65*45])
            permuted_subjRDM_brain[:] = np.nan
            permuted_subjRDM_brain[list(permuted_subjRDM.rdm_descriptors['voxel_index'])] = permuted_eval_score
            permuted_subjRDM_brain = permuted_subjRDM_brain.reshape([53, 65, 45])
            permuted_rslt[i,:] = permuted_subjRDM_brain
        
        np.save('RSA_result/subject_RSA_permutation/sub{}_RSA_result_permutation.npy'.format(s), permuted_rslt)

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

    # make a folder to save results
    if not os.path.exists('RSA_result'):
        os.mkdir('RSA_result')

    # compute permutations    
    num_permutation = 1000
    run_RSA(num_permutation) 

    # run the statistical analysis
    RSA_statistics(1000)