import os
import earthaccess

os.environ["EARTHDATA_USERNAME"] = "lfegray"
os.environ["EARTHDATA_PASSWORD"] = "gugdo4-dapGuf-ximcev"


us_coords = (-124.77, 24.52, -66.95, 49.38)
start_date = "2023-08-01"
end_date =  "2023-08-03"
# end_date =  "2023-09-01"


def download_dataset(name, doi):
    results = earthaccess.search_data(
        doi = doi,
        bounding_box=us_coords,
        temporal=(start_date, end_date),
    )

    path = f"./data/{name}"
    if os.path.exists(path):
        files = earthaccess.download(results, path)

    else:
        os.makedirs(path)
        files = earthaccess.download(results, path)


if __name__ == "__main__":

    download_dataset("moisture", "10.5067/EVKPQZ4AFC4D")
    # download_dataset("nvdi_and_evi", "10.5067/MODIS/MOD13A2.061")
    download_dataset("sif", "10.5067/NOD1DPPBCXSO")





