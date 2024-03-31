from joblib import dump, load as jload
from os import path
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from Data import get_split_data


# Directory path
dir_path: str = path.dirname(path.realpath(__file__))

# Name of the model file, without extension
save_file: str = "lr_model"


def simple_train(
        x_test: DataFrame,
        x_train: DataFrame,
        y_train: DataFrame) -> tuple[Pipeline, DataFrame]:
    """

    Args:
        x_test: X_test dataset.
        x_train: X_train dataset.
        y_train: Y_train dataset.

    Returns:
        The model pipline along with the predicted dataframe.

    """

    # Scale the numeric features (all the features in our case), and then pass to model
    pipeline: Pipeline = Pipeline([
        ('scaler', StandardScaler().set_output(transform="pandas")),
        ('model', LinearRegression())
    ])

    # LR model
    pipeline.fit(x_train, y_train)

    return pipeline, DataFrame(pipeline.predict(x_test), columns=["high", "low", "close"])


def test(n: int) -> list[float]:
    """

    Args:
        n: Number of K-Folds to perform.

    Returns:
        List of R2 scores for each iteration.

    """

    X, y = get_split_data()
    res: list[float] = []

    # Assuming your data is in X and y
    tscv = TimeSeriesSplit(n_splits=n)  # Use the number of splits you prefer

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        _, y_pred = simple_train(X_test, X_train, y_train)

        res.append(r2_score(y_test, y_pred))

    return res


def train(no_save: bool = False) -> tuple[Pipeline, float]:
    """

    Trains the model and saves it to its designated file.

    Args:
        no_save: True to not save the trained model.

    Returns:
        The trained model along with its R2 score.

    """
    X, y = get_split_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    pipeline, y_pred = simple_train(X_test, X_train, y_train)

    # Evaluate the model
    if not no_save:
        dump(pipeline, path.join(dir_path, f"{save_file}.sav"))

    return pipeline, r2_score(y_test, y_pred)


def load() -> Pipeline:
    """

    Returns:
        The loaded model from the designated file.

    """
    return jload(path.join(dir_path, f"{save_file}.sav"))
