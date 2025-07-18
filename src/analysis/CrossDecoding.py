from nilearn.decoding import DecoderRegressor
from sklearn.model_selection import LeaveOneGroupOut

def crossdecode(
    beta_maps_train,
    beta_maps_test,
    logk_diff,
    subject_ids_train,
    mask,
    scoring="neg_mean_absolute_error"
):
    """
    Trains an SVR DecoderRegressor on individual beta maps and predicts logk_diff.
    """
    decoder = DecoderRegressor(
        estimator="svr",
        mask=mask,
        scoring=scoring,
        standardize="zscore_sample", 
        cv=LeaveOneGroupOut()
    )

    decoder.fit(beta_maps_train, logk_diff, groups=subject_ids_train)
    pred_train = decoder.predict(beta_maps_train)
    pred_test = decoder.predict(beta_maps_test)

    return pred_train, pred_test, decoder
