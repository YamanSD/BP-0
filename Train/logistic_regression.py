from joblib import dump, load as jload
from os import path

from numpy import ravel, ndarray
from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score  # Check for other testing methods
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from Data import get_data

# Directory path
dir_path: str = path.dirname(path.realpath(__file__))

# Name of the model file, without extension
save_file: str = "lgr_model"


def scale(df: DataFrame, scaler: StandardScaler = None) -> DataFrame:
    """

    Args:
        df: DataFrame to scale.
        scaler: Optional StandardScaler to use.

    Returns:
        A scaled DataFrame suitable for use of predictions by the model.

    """

    if scaler is None:
        scaler = StandardScaler().set_output(transform="pandas")

    return scaler.transform(df)


def get_split_data() -> tuple[DataFrame, ndarray]:
    """

    Returns:
        Overrides the usual split, due to the single-dependent-variable nature of LogisticRegression.

    """
    df: DataFrame = get_data()

    return (
        df.drop(['close', 'high', 'low'], axis=1),
        ravel(
            (df['open'] - df['close']).map(lambda v: -1 if v < 0 else int(0 < v))
        )
    )


def simple_train(x_test: DataFrame, x_train: DataFrame, y_train: DataFrame) -> tuple[LogisticRegression, DataFrame]:
    """

    Args:
        x_test: X_test dataset.
        x_train: X_train dataset.
        y_train: Y_train dataset.

    Returns:
        The model along with the predicted dataframe.

    """

    # Scale the numeric features (all the features in our case)
    scaler: StandardScaler = StandardScaler().set_output(transform="pandas")

    x_train = scaler.fit_transform(x_train)
    x_test = scale(x_test, scaler)

    # LR model
    regressor: LogisticRegression = LogisticRegression(max_iter=400)
    regressor.fit(x_train, y_train)

    return regressor, DataFrame(regressor.predict(x_test), columns=["direction"])


def test(n: int) -> list[float]:
    """

    Args:
        n: Number of K-Folds to perform.

    Returns:
        List of accuracy scores for each iteration.

    """

    X, y = get_split_data()
    res: list[float] = []

    # Assuming your data is in X and y
    tscv = TimeSeriesSplit(n_splits=n)  # Use the number of splits you prefer

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y[train_index], y[test_index]

        _, y_pred = simple_train(X_test, X_train, y_train)

        res.append(accuracy_score(y_test, y_pred))

    return res


def train(no_save: bool = False) -> (LogisticRegression, float):
    """

    Trains the model and saves it to its designated file.

    Args:
        no_save: True to not save the trained model.

    Returns:
        The trained model along with its accuracy score.

    """
    X, y = get_split_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    regressor, y_pred = simple_train(X_test, X_train, y_train)

    # Evaluate the model
    if not no_save:
        dump(regressor, path.join(dir_path, f"{save_file}.sav"))

    return regressor, accuracy_score(y_test, y_pred)


def load() -> LogisticRegression:
    """

    Returns:
        The loaded model from the designated file.

    """
    return jload(path.join(dir_path, f"{save_file}.sav"))
