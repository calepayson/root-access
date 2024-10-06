import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def load_formatted_sif_moisture_data(file_path='sif_moisture.parquet'):
    # Read the Parquet file
    df = pd.read_parquet(file_path)
    
    # Convert the 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort the dataframe by date
    df = df.sort_values('date')
    
    # Print info about the loaded data
    print(f"Loaded {len(df)} rows of data.")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print("\nColumn info:")
    print(df.info())
    
    
    return df

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def linear_fit_sif(df):
    # Select features (X) and target variable (y)
    features = ['sif_lat', 'sif_lon', 'water_prev1', 'root_water_prev1', 'water_prev2',
                'root_water_prev2', 'water_prev3', 'root_water_prev3']
    X = df[features]
    y = df['sif_value']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    # Print feature coefficients
    for feature, coef in zip(features, model.coef_):
        print(f"{feature}: {coef}")

    print(f"\nIntercept: {model.intercept_}")
    print(f"Mean Squared Error: {mse}")
    print(f"Root Mean Squared Error: {rmse}")
    print(f"R-squared Score: {r2}")
    print(f"Mean of sif_value: {np.mean(y)}")
    print(f"Standard deviation of sif_value: {np.std(y)}")

    return model, X_test, y_test, y_pred

# Usage example:
# df = pd.read_csv('your_data.csv')  # Load your data
# model, X_test, y_test, y_pred = linear_fit_sif(df)


if __name__ == "__main__":

    df = load_formatted_sif_moisture_data()

    model, X_test, y_test, y_pred = linear_fit_sif(df)
