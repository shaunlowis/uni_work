""" Author: Johnny (Shaun) Lowis, for Bodeker Scientific.
Example of multivariate linear regression model, example data and code guide followed from:
https://towardsdatascience.com/a-beginners-guide-to-linear-regression-in-python-with-scikit-learn-83a8f7ae2b4f """

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from users.sl_scripts.Regression.instrument_regression import regress
from sklearn import metrics


def read_csv(fp):
    data = pd.read_csv(fp)
    data.isnull().any()
    dataset = data.fillna(method='ffill')
    X = dataset[['fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar', 'chlorides', 'free sulfur '
                 'dioxide', 'total sulfur dioxide', 'density', 'pH', 'sulphates', 'alcohol']].values
    y = dataset['quality'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    return X_train, X_test, y_train, y_test


def error(y_test, y_pred):
    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))


def main():
    fp = r"/home/slowis/Documents/regression/winequality.csv"
    X_train, X_test, y_train, y_test = read_csv(fp)
    y_pred = regress(X_train, X_test)
    error(y_test, y_pred)


if __name__ == '__main__':
    main()
