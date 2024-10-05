import h5py
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

def process_smap_l4_file(file_path):
    with h5py.File(file_path, 'r') as f:
        # Extract date and time from filename
        datetime_str = file_path.split('_')[-3]
        date_time = datetime.strptime(datetime_str, '%Y%m%dT%H%M%S')
        print(f"Processing {date_time}...")
        
        # Read relevant datasets
        surface_soil_moisture = f['/Geophysical_Data/sm_surface'][:]
        root_zone_soil_moisture = f['/Geophysical_Data/sm_rootzone'][:]
        latitude = f['/cell_lat'][:]
        longitude = f['/cell_lon'][:]
        
        # Flatten arrays
        surface_soil_moisture = surface_soil_moisture.flatten()
        root_zone_soil_moisture = root_zone_soil_moisture.flatten()
        latitude = latitude.flatten()
        longitude = longitude.flatten()
        
        # Create DataFrame
        df = pd.DataFrame({
            'date_time': date_time,
            'latitude': latitude,
            'longitude': longitude,
            'surface_soil_moisture': surface_soil_moisture,
            'root_zone_soil_moisture': root_zone_soil_moisture
        })
        
        # Remove fill values (assuming -9999.0 is still used as fill value)
        df = df[(df['surface_soil_moisture'] != -9999.0) & (df['root_zone_soil_moisture'] != -9999.0)]
        
        # Filter for USA
        df = df[(df['latitude'] >= US_BBOX['min_lat']) & (df['latitude'] <= US_BBOX['max_lat']) &
                (df['longitude'] >= US_BBOX['min_lon']) & (df['longitude'] <= US_BBOX['max_lon'])]
        
        return df


if __name__ == "__main__":
    # Process all files
    data_path = "./data/moisture"

    all_files = sorted(glob(os.path.join(data_path, 'SMAP_L4_SM_gph_*.h5')))
    print(f"Processing {len(all_files)} granules...")
    all_data = [process_smap_l4_file(file) for file in all_files]

    # Concatenate all data
    final_df = pd.concat(all_data, ignore_index=True)

    # Save to parquet format
    final_df.to_parquet('moisture.parquet')
    
    print(f"Processed data saved. Total rows: {len(final_df)}")
