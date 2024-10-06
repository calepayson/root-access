import netCDF4
import os
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime

US_BBOX = {
    'min_lat': 24.396308,
    'max_lat': 49.384358,
    'min_lon': -125.0,
    'max_lon': -66.93457
}

def process_oco3_sif_file(file_path):
    with netCDF4.Dataset(file_path, 'r') as nc:
        # Print out all variable names
        print("Available variables:", list(nc.variables.keys()))

        # Extract date from filename
        filename = os.path.basename(file_path)
        date_str = filename.split('_')[2]
        date = datetime.strptime(date_str, '%y%m%d')
        print(f"Processing {date}...")

        # Read relevant datasets
        latitude = nc.variables['Latitude'][:]
        longitude = nc.variables['Longitude'][:]
        sif = nc.variables['Daily_SIF_757nm'][:]  # Using Daily SIF at 757nm
        sif_uncertainty = nc.variables['SIF_Uncertainty_740nm'][:]  # Using uncertainty at 740nm as a proxy
        quality_flag = nc.variables['Quality_Flag'][:]

        # Create DataFrame
        df = pd.DataFrame({
            'date': date,
            'latitude': latitude,
            'longitude': longitude,
            'sif': sif,
            'sif_uncertainty': sif_uncertainty,
            'quality_flag': quality_flag
        })

        # Remove fill values (you may need to adjust this based on the actual fill value)
        df = df[(df['sif'] > -1e30) & (df['sif_uncertainty'] > -1e30)]

        # Filter for good quality data (adjust as needed based on the meaning of Quality_Flag)
        df = df[df['quality_flag'] == 0]  # Assuming 0 means good quality

        # Filter for USA
        df = df[(df['latitude'] >= US_BBOX['min_lat']) & (df['latitude'] <= US_BBOX['max_lat']) &
                (df['longitude'] >= US_BBOX['min_lon']) & (df['longitude'] <= US_BBOX['max_lon'])]

        return df

if __name__ == "__main__":
    # Process all files
    data_path = "./data/sif"

    all_files = sorted(glob(os.path.join(data_path, 'oco3_LtSIF_*.nc4')))
    print(f"Processing {len(all_files)} files...")
    all_data = [process_oco3_sif_file(file) for file in all_files]

    # Concatenate all data
    final_df = pd.concat(all_data, ignore_index=True)

    # Save to parquet format
    final_df.to_parquet('oco3_sif.parquet')
    
    print(f"Processed data saved. Total rows: {len(final_df)}")
