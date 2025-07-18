from sklearn.model_selection import LeaveOneGroupOut
from nilearn.decoding import SearchLight
import numpy as np
import os
import nibabel as nib

def run_searchlight_condition_maps(df, condition, mask_img, scorer="explained_variance", outdir="searchlight_results"):
    """
    Run searchlight for a given condition and return/save results per subject.

    Parameters:
        df: pandas DataFrame with columns ['subjid', 'beta_map', 'SV', 'run']
        condition: string, "short" or "long"
        mask_img: a binary NIfTI mask image (nibabel object)
        outdir: directory to save output .nii.gz files
    """
    os.makedirs(outdir, exist_ok=True)
    all_scores = {}
    all_maps = {}

    # Filter by condition
    df_condition = df[df['condition'] == condition]

    # Loop through subjects
    for sub in df_condition['subjid'].unique():
        print(f"Running subject: {sub}, condition: {condition}")

        df_sub = df_condition[df_condition['subjid'] == sub]
        groups = df_sub['run']
        beta_maps = df_sub['beta_map'].tolist()
        sv_values = df_sub['SV'].values

        sl = SearchLight(
            mask_img=mask_img,
            radius=10,
            estimator='svr',
            scoring=scorer,
            cv=LeaveOneGroupOut(),
            n_jobs=-1,
            verbose=1
        )

        sl.fit(beta_maps, sv_values, groups=groups)
        scores = sl.scores_  # 3D NumPy array

        all_scores[sub] = scores

        # Save as NIfTI
        out_img = nib.Nifti1Image(scores, affine=mask_img.affine)
        out_fname = f"searchlight_{condition}_{sub}_{scorer}_map.nii.gz"
        out_path = os.path.join(outdir, out_fname)
        nib.save(out_img, out_path)

        all_maps[sub] = out_img  # not just scores

    return all_scores, all_maps