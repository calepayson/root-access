import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from datetime import timedelta

def process_sif_moisture_data(sif_file, moisture_file, n_days=3):
    # Load data
    sif_df = pd.read_parquet(sif_file)
    moisture_df = pd.read_parquet(moisture_file)

    # Convert 'date' columns to datetime
    sif_df['date'] = pd.to_datetime(sif_df['date']).dt.date
    moisture_df['date'] = pd.to_datetime(moisture_df['date_time']).dt.date

    # Sort dataframes by date
    sif_df = sif_df.sort_values('date')
    moisture_df = moisture_df.sort_values('date')

    # Get date ranges
    sif_start, sif_end = sif_df['date'].min(), sif_df['date'].max()
    moisture_start, moisture_end = moisture_df['date'].min(), moisture_df['date'].max()

    print(f"SIF date range: {sif_start} to {sif_end}")
    print(f"Moisture date range: {moisture_start} to {moisture_end}")

    # Filter moisture data to relevant date range
    moisture_df = moisture_df[(moisture_df['date'] >= sif_start - timedelta(days=n_days)) &
                              (moisture_df['date'] <= sif_end)]

    # Group moisture data by date
    moisture_groups = moisture_df.groupby('date')

    # Build KDTree for each date in moisture data
    moisture_KDTree_dict = {}
    for date, group in moisture_groups:
        lat_lons = group[['latitude', 'longitude']].values
        tree = cKDTree(lat_lons)
        moisture_KDTree_dict[date] = {
            'tree': tree,
            'moisture_values': group[['surface_soil_moisture', 'root_zone_soil_moisture']].values
        }

    results = []
    for _, row in sif_df.iterrows():
        sif_date = row['date']
        sif_lat, sif_lon = row['latitude'], row['longitude']
        
        result_row = {
            'date': sif_date,
            'sif_lat': sif_lat,
            'sif_lon': sif_lon,
            'sif_value': row['sif']
        }

        for k in range(1, n_days + 1):
            date_k = sif_date - timedelta(days=k)
            key = f'water_prev{k}'
            root_key = f'root_water_prev{k}'
            
            if date_k in moisture_KDTree_dict:
                tree = moisture_KDTree_dict[date_k]['tree']
                moisture_values = moisture_KDTree_dict[date_k]['moisture_values']

                dist, idx_nn = tree.query([[sif_lat, sif_lon]], k=1)
                moisture_value = moisture_values[idx_nn[0]]
                
                result_row[key] = moisture_value[0]
                result_row[root_key] = moisture_value[1]
            else:
                result_row[key] = np.nan
                result_row[root_key] = np.nan

        results.append(result_row)

    final_df = pd.DataFrame(results)
    initial_rows = len(final_df)
    final_df = final_df.dropna()
    rows_removed = initial_rows - len(final_df)
    print(f"Removed {rows_removed} rows containing NA values.")

    return final_df


def create_dummy_inference_data(moisture_file, n_days=3):
    # Load moisture data
    moisture_df = pd.read_parquet(moisture_file)
    
    # Convert 'date' column to datetime
    moisture_df['date'] = pd.to_datetime(moisture_df['date_time']).dt.date
    
    # Get the most recent date
    most_recent_date = moisture_df['date'].max()
    
    # Filter data for the most recent date
    recent_moisture = moisture_df[moisture_df['date'] == most_recent_date]
    
    # Create the dummy inference dataframe
    dummy_inference = pd.DataFrame({
        'date': recent_moisture['date'],
        'sif_lat': recent_moisture['latitude'],
        'sif_lon': recent_moisture['longitude'],
        'sif_value': 0  # Fill with zeros as per requirement
    })
    
    # Add moisture data columns
    for i in range(1, n_days + 1):
        dummy_inference[f'water_prev{i}'] = recent_moisture['surface_soil_moisture']
        dummy_inference[f'root_water_prev{i}'] = recent_moisture['root_zone_soil_moisture']
    
    # Convert date to string for consistency with the main dataframe
    dummy_inference['date'] = dummy_inference['date'].astype(str)
    
    print(f"Created dummy inference data with {len(dummy_inference)} rows for date {most_recent_date}")
    print(dummy_inference.info())
    
    return dummy_inference




if __name__ == "__main__":

    sif_file = 'oco3_sif.parquet'
    moisture_file = 'moisture.parquet'

    final_df = process_sif_moisture_data(sif_file, moisture_file, n_days=3)
    final_df['date'] = final_df['date'].astype(str)
    print(final_df.info())
    final_df.to_parquet('sif_moisture.parquet')

    dummy_inference_df = create_dummy_inference_data(moisture_file, n_days=3)

    # Save dummy inference data to parquet
    dummy_inference_df.to_parquet('dummy_inference_data.parquet')
    print("Dummy inference data saved to dummy_inference_data.parquet")
