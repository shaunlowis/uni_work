""" Author: Johnny (Shaun) Lowis, for Bodeker Scientific.
Example of simple two variable linear regression model, example data and code guide followed from:
https://towardsdatascience.com/a-beginners-guide-to-linear-regression-in-python-with-scikit-learn-83a8f7ae2b4f """

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics


def read_data(fp):
    data = pd.read_csv(fp)
    X = data['MinTemp'].values.reshape(-1, 1)
    y = data['MaxTemp'].values.reshape(-1, 1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    return X_train, X_test, y_train, y_test


def regress(x_train, x_test, y_train, y_test):
    regressor = LinearRegression()
    regressor.fit(x_train, y_train)
    y_pred = regressor.predict(x_test)
    df = pd.DataFrame({'Actual': y_test.flatten(), 'Predicted': y_pred.flatten()})
    df1 = df.head(25)
    df1.plot(kind='bar', figsize=(16, 10))
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='green')
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    plt.show()
    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    # To retrieve the intercept:
    print(regressor.intercept_)  # For retrieving the slope:
    print(regressor.coef_)


def main():
    fp = r"/home/slowis/Documents/regression/Weather.csv"
    X_train, X_test, y_train, y_test = read_data(fp)
    regress(X_train, X_test, y_train, y_test)


main()
