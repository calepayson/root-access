import os

import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib


def load_formatted_sif_moisture_data(file_path='sif_moisture.parquet'):
    df = pd.read_parquet(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Print info about the loaded data
    print(f"Loaded {len(df)} rows of data.")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print("\nColumn info:")
    print(df.info())

    return df


def linear_fit(df):
    features = ['sif_lat', 'sif_lon', 'water_prev1', 'root_water_prev1', 'water_prev2',
                'root_water_prev2', 'water_prev3', 'root_water_prev3']

    X = df[features]
    y = df['sif_value']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    for feature, coef in zip(features, model.coef_):
        print(f"{feature}: {coef}")

    print(f"Mean Squared Error: {mse}")
    print(f"Root Mean Squared Error: {rmse}")
    print(f"R-squared Score: {r2}")
    print(f"Mean of sif_value: {np.mean(y)}")
    print(f"Standard deviation of sif_value: {np.std(y)}")

    return model


class ModelWrapper:
    def __init__(self, fit_fn: callable):
        self.fit_fn = fit_fn
        self.model_name = fit_fn.__name__

        if os.path.exists(f"{self.model_name}.joblib"):
            print(f"Loading model from {self.model_name}.joblib")
            self.model = joblib.load(f"{self.model_name}.joblib")
        else:
            print(f"Fitting model {self.model_name}")
            self.fit()

    def fit(self):
        df = load_formatted_sif_moisture_data()
        self.model = self.fit_fn(df)

    def save(self):
        joblib.dump(self.model, f"{self.model_name}.joblib")

    def load(self, path:str):
        self.model = joblib.load(path)

    def predict(self, X):
        return self.model.predict(X)



if __name__ == "__main__":


    model = ModelWrapper(linear_fit)
    model.save()

    # perform inference on whole df
    df = load_formatted_sif_moisture_data()

    X = df[['sif_lat', 'sif_lon', 'water_prev1', 'root_water_prev1', 'water_prev2',
            'root_water_prev2', 'water_prev3', 'root_water_prev3']]

    y = df['sif_value']

    y_pred = model.predict(X)

    # substitute the predicted values in the dataframe
    df['sif_value'] = y_pred

    # save the dataframe with the predicted values
    df.to_parquet('sif_moisture_predicted.parquet')


