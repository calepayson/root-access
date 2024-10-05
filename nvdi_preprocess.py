import h5py
import os
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime
from datetime import timedelta

US_BBOX = {
    'min_lat': 24.396308,
    'max_lat': 49.384358,
    'min_lon': -125.0,
    'max_lon': -66.93457
}

def parse_filename(filename):
    parts = filename.split('.')
    date_str = parts[1][1:]  # Remove the 'A' prefix
    year = int(date_str[:4])
    doy = int(date_str[4:])
    tile = parts[2]
    return datetime(year, 1, 1) + timedelta(days=doy - 1), tile

def process_modis_ndvi_file(file_path):
    filename = os.path.basename(file_path)
    date, tile = parse_filename(filename)
    print(f"Processing {filename} for date {date}, tile {tile}")

    with h5py.File(file_path, 'r') as f:
        # Read relevant datasets
        ndvi = f['/MODIS_Grid_16DAY_1km_VI/Data Fields/1 km 16 days NDVI'][:]
        evi = f['/MODIS_Grid_16DAY_1km_VI/Data Fields/1 km 16 days EVI'][:]
        quality = f['/MODIS_Grid_16DAY_1km_VI/Data Fields/1 km 16 days VI Quality'][:]
        reliability = f['/MODIS_Grid_16DAY_1km_VI/Data Fields/1 km 16 days pixel reliability'][:]

        # Read geolocation data
        ydim, xdim = ndvi.shape
        
        upper_left_x = f['/MODIS_Grid_16DAY_1km_VI'].attrs['UpperLeftPointMtrs'][0]
        upper_left_y = f['/MODIS_Grid_16DAY_1km_VI'].attrs['UpperLeftPointMtrs'][1]
        
        # Calculate lat/lon for each pixel (approximate method)
        x_coords = np.linspace(upper_left_x, upper_left_x + xdim * 1000, xdim)
        y_coords = np.linspace(upper_left_y, upper_left_y - ydim * 1000, ydim)
        lon, lat = np.meshgrid(x_coords, y_coords)
        
        # Convert to degrees (very approximate, assumes spherical Earth)
        R_earth = 6371007.181  # Earth radius in meters
        lat_deg = np.degrees(lat / R_earth)
        lon_deg = np.degrees(lon / (R_earth * np.cos(np.radians(lat_deg))))

        # Flatten arrays
        ndvi = ndvi.flatten()
        evi = evi.flatten()
        quality = quality.flatten()
        reliability = reliability.flatten()
        lat_deg = lat_deg.flatten()
        lon_deg = lon_deg.flatten()

        # Create DataFrame
        df = pd.DataFrame({
            'date': date,
            'tile': tile,
            'latitude': lat_deg,
            'longitude': lon_deg,
            'ndvi': ndvi,
            'evi': evi,
            'quality': quality,
            'reliability': reliability
        })

        # Remove fill values
        df = df[(df['ndvi'] != -3000) & (df['evi'] != -3000)]

        # Apply scale factor to NDVI and EVI
        df['ndvi'] = df['ndvi'] * 0.0001
        df['evi'] = df['evi'] * 0.0001

        # Filter for USA
        df = df[(df['latitude'] >= US_BBOX['min_lat']) & (df['latitude'] <= US_BBOX['max_lat']) &
                (df['longitude'] >= US_BBOX['min_lon']) & (df['longitude'] <= US_BBOX['max_lon'])]

        return df

if __name__ == "__main__":
    # Process all files
    data_path = "./data/nvdi_and_evi"

    all_files = sorted(glob(os.path.join(data_path, 'MOD13A2.A*.hdf')))
    print(f"Found {len(all_files)} files to process...")
    all_data = [process_modis_ndvi_file(file) for file in all_files]

    # Concatenate all data
    final_df = pd.concat(all_data, ignore_index=True)

    # Save to parquet format
    final_df.to_parquet('ndvi_evi.parquet')

    print(f"Processed data saved. Total rows: {len(final_df)}")
