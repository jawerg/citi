import time
from copy import deepcopy

import numpy as np
import pandas as pd
import sklearn
import sklearn.metrics as metrics
import statsmodels.api as sm
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import train_test_split

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Globals
FRAC_SAMPLE = 1.0  # should be 1.0 in final version ;)
FRAC_TEST_DATA = 0.2  # ToDo: Find reasonable size.

MODELS = [
    sklearn.linear_model.LogisticRegression(max_iter=10000),
    sklearn.tree.DecisionTreeClassifier(),
    sklearn.ensemble.BaggingClassifier(
        sklearn.tree.DecisionTreeClassifier(),
        max_samples=0.5,
        max_features=1.0,
        n_estimators=10,
    ),
    sklearn.ensemble.AdaBoostClassifier(
        sklearn.tree.DecisionTreeClassifier(min_samples_split=10, max_depth=4),
        n_estimators=10,
        learning_rate=0.6,
    ),
    sklearn.ensemble.RandomForestClassifier(n_estimators=30, max_depth=9),
]


def generate_dataset_from_feature_file(filepath: str) -> list[pd.DataFrame]:
    # Load data
    data = pd.read_parquet(filepath)
    data.columns = [col.lower().replace("_", " ") for col in data.columns]
    data = data.sample(frac=FRAC_SAMPLE)

    # Translate object datatypes into floats
    data["customer age"] = data["customer age"].astype(float)
    data["tripduration in h"] = data["tripduration in h"].astype(float)

    # Generate some interactions of trip speed in kmh as most valuable variable in
    # estimation
    col = "trip speed kmh"
    data["age       x speed"] = data["customer age"] * data[col]
    data["distance  x speed"] = data["trip distance in km"] * data[col]
    data["feelslike x speed"] = data["feelslike"] * data[col]

    # split into endogenous and exogenous variables.
    X = data.loc[:, data.columns != "is subscriber"]
    y = data.loc[:, data.columns == "is subscriber"]

    # Prepare some dtypes as those are loaded as object type.
    y = (y["is subscriber"] == "Subscriber").astype(np.uint8)

    # Add constant for regression
    X = sm.add_constant(X)

    # loop over each categorical variable to construct binary ones.
    categorical_variables_with_baseline = {
        "gender": "male",
        "start dow": "0 sunday",
        "start hour": "8",
        "start month": "05 may",
    }

    for var, base_cat in categorical_variables_with_baseline.items():
        category_df = pd.get_dummies(X[var], prefix=var)
        category_df.columns = [col.lower().replace("_", ": ") for col in category_df]
        X = pd.concat([X, category_df], axis=1)

        # construct baseline full name and drop it.
        baseline_name = f"{var}: {base_cat}"
        X = X.drop(baseline_name, axis=1)  # remove base category

        # Drop generator variable
        X = X.drop(var, axis=1)

    # Generate Training and Test dataset
    Xt, Xtt, yt, ytt = train_test_split(X, y, test_size=FRAC_TEST_DATA, random_state=0)
    yt, ytt = yt.astype("int"), ytt.astype("int")

    # Undersampling
    rus = RandomUnderSampler(random_state=0, sampling_strategy=1.0)
    Xt, yt = rus.fit_resample(Xt, yt)

    return [Xt, yt, Xtt, ytt]  # use identical order for downstream functions


def get_model_name(model) -> str:
    return str(type(model)).split('.')[-1].replace("'>", "")


def compute_scores_for_models(Xt, yt, Xtt, ytt):
    # get copy of global variable for models.
    models = deepcopy(MODELS)

    # Compute different Scores for each estimator
    df_scores = pd.DataFrame()
    for mod in models:
        # generate minimal output
        start_time = time.time()

        # fit model and predict y_hat for test data.
        mod.fit(Xt, yt)
        ytt_hat = mod.predict(Xtt)

        # report current model and needed time.
        est_time = time.time() - start_time
        print(f"Estimated {get_model_name(mod)} in {est_time:3.2f} seconds")

        # compute several metrics to compare
        df_mod = pd.DataFrame.from_dict(
            {
                "Accuracy": np.round([metrics.accuracy_score(ytt, ytt_hat)], 3),
                "Precision": np.round([metrics.precision_score(ytt, ytt_hat)], 3),
                "Recall": np.round([metrics.recall_score(ytt, ytt_hat)], 3),
                "F1-Score": np.round([metrics.f1_score(ytt, ytt_hat)], 3),
                "ROC AUC": np.round([metrics.roc_auc_score(ytt, ytt_hat)], 3),
            },
            orient="columns",
        )
        df_mod.index = [get_model_name(mod)]
        df_scores = pd.concat([df_scores, df_mod], axis=0)
    return models, df_scores
