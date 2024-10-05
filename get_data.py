import os
import earthaccess

os.environ["EARTHDATA_USERNAME"] = "lfegray"
os.environ["EARTHDATA_PASSWORD"] = "gugdo4-dapGuf-ximcev"


us_coords = (-124.77, 24.52, -66.95, 49.38)
start_date = "2024-09-01"
end_date =  "2024-09-14"


def download_dataset(name, doi):
    results = earthaccess.search_data(
        doi = doi,
        bounding_box=us_coords,
        temporal=(start_date, end_date),
    )

    files = earthaccess.download(results, f"./data/{name}")



if __name__ == "__main__":

    download_dataset("moisture", "10.5067/EVKPQZ4AFC4D")
