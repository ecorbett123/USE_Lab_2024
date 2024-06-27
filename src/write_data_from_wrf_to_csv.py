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
        np.savetxt('lat_array.csv', lats_np, delimiter=',')
        np.savetxt('lon_array.csv', lons_np, delimiter=',')
        np.savetxt('t2_array.csv', t2_np, delimiter=',')

        # Get the cartopy projection
        # cart_proj = get_cartopy(var)
        #
        # # Create the plot
        # fig = plt.figure(figsize=(12, 9))
        # ax = plt.axes(projection=cart_proj)
        # # Remove the existing coastline feature
        # # Add a detailed coastline feature with a solid line
        # ax.add_feature(cfeature.COASTLINE, linewidth=0.8, linestyle='-')
        # ax.add_feature(cfeature.BORDERS, linewidth=0.5)
        # ax.add_feature(cfeature.STATES, linestyle=':', linewidth=0.5)
        #
        # # Plot the variable
        # contour = plt.contourf(to_np(lons), to_np(lats), to_np(var), cmap="jet", transform=crs.PlateCarree())
        #
        # # Add colorbar
        # plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.05, aspect=50)
        #
        # # Set plot extent
        # ax.set_extent([to_np(lons).min(), to_np(lons).max(), to_np(lats).min(), to_np(lats).max()])
        #
        # # Update plot title with the current time
        # plt.title(f"{variable_name} at {time}")
        #
        # # Display the plot
        # plt.show()


# Paths to the wrfout files for domains d02 and d03
file_paths = [
    r"/Users/emmacorbett/PycharmProjects/USE_Lab/wrfout_d01_2024-06-04_00_00_00",
    r"/Users/emmacorbett/PycharmProjects/USE_Lab/wrfout_d02_2024-06-04_00_00_00",
    r"/Users/emmacorbett/PycharmProjects/USE_Lab/wrfout_d03_2024-06-04_00_00_00"
]

# Visualize a common variable, e.g., 2-meter temperature (T2)
for file_path in file_paths:
    visualize_wrf_output(file_path, "T2")
