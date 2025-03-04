import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import getvar, to_np, latlon_coords, get_cartopy, extract_times
import cartopy.crs as crs
import cartopy.feature as cfeature

# NOTE: need to run in another anaconda environment that supports the necessary packages above ^

def visualize_wrf_output(file_path, variable_name):
    # Open the NetCDF file
    ncfile = Dataset(file_path)

    # Extract all available times
    times = extract_times(ncfile, timeidx=None)

    # Loop through each time step and plot the variable
    for time_idx, time in enumerate(times):
        # Extract the desired variable for the current time step
        var = getvar(ncfile, variable_name, timeidx=time_idx)

        # Get the latitude and longitude points
        lats, lons = latlon_coords(var)

        lats_np = to_np(lats)
        lons_np = to_np(lons)
        t2_np = to_np(var)

        # write lat, lon, and vars to csv files
        np.savetxt('lat_array_2.csv', lats_np, delimiter=',')
        np.savetxt('lon_array_2.csv', lons_np, delimiter=',')
        np.savetxt('t2_array_2.csv', t2_np, delimiter=',')


# Paths to the wrfout files for domains d02 and d03
file_paths = [
    r"/Users/emmacorbett/PycharmProjects/USE_Lab/data/wrf_heat_maps/aug5_2024/wrfout_d01_2024-06-20_00_00_00",
    r"/Users/emmacorbett/PycharmProjects/USE_Lab/data/wrf_heat_maps/aug5_2024/wrfout_d02_2024-06-20_00_00_00",
    r"/Users/emmacorbett/PycharmProjects/USE_Lab/data/wrf_heat_maps/aug5_2024/wrfout_d03_2024-06-20_00_00_00"
]

# Visualize a common variable, e.g., 2-meter temperature (T2)
for file_path in file_paths:
    visualize_wrf_output(file_path, "T2")
