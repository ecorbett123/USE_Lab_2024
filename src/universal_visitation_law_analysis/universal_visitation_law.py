import matplotlib.pyplot as plt
import pandas as pd
import math
from geopy.distance import geodesic
import json
import os

# Constants
LATITUDE_DEGREE_METERS = 111320  # meters per degree of latitude
LONGITUDE_DEGREE_METERS_AT_40_7N = 85390  # meters per degree of longitude at 40.7° N

# Grid size in meters
grid_size_meters = 500

# Calculate degrees per 500 meters
lat_step = grid_size_meters / LATITUDE_DEGREE_METERS
lon_step = grid_size_meters / (LONGITUDE_DEGREE_METERS_AT_40_7N * math.cos(math.radians(40.7)))

# Define the boundaries of New York City
lat_min, lat_max = 40.4774, 40.9176
lon_min, lon_max = -74.2591, -73.7004


# Function to determine the grid cell and its boundaries for a given latitude and longitude
def get_grid_cell_with_center(lat, lon, a_lat_min, a_lon_min, a_lat_step, a_lon_step, grid_cells):
    lat_index = int((lat - a_lat_min) / a_lat_step)
    lon_index = int((lon - a_lon_min) / a_lon_step)
    cell_lat_min = a_lat_min + lat_index * a_lat_step
    cell_lat_max = cell_lat_min + a_lat_step
    cell_lon_min = a_lon_min + lon_index * a_lon_step
    cell_lon_max = cell_lon_min + a_lon_step
    if (lat_index, lon_index) not in grid_cells:
        grid_cells[str(lat_index) + "," + str(lon_index)] = ((cell_lat_min+cell_lat_max)/2, (cell_lon_min+cell_lon_max)/2)
    return str(lat_index) + "," + str(lon_index)


def is_valid_location(lat, lon):
    if not lat or not lon:
        return False
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


# Function to calculate distance between two lat/lng pairs
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters


def normalize(num_rides, bucket):
    num = num_rides/((2*math.pi* ((bucket.right/500)**2 - ((bucket.left/500)**2))))
    return 0 if num == 0 else math.log10(num)


# read in dataframe - time period = 1 month (july)
csv_directory = '/Users/emmacorbett/PycharmProjects/USE_Lab/data/Citibike/5_May_2024'
#csv_directory = '/Users/emmacorbett/PycharmProjects/USE_Lab/data/Citibike/test'
# Uncomment out the below to create the initial distances file (takes like 10min to run)
# List to store individual DataFrames
# dataframes = []
#
# # Loop through each file in the directory
# for filename in os.listdir(csv_directory):
#     if filename.endswith('.csv'):
#         # Full path of the CSV file
#         file_path = os.path.join(csv_directory, filename)
#
#         # Read the CSV file into a DataFrame
#         df = pd.read_csv(file_path)
#
#         # Append the DataFrame to the list
#         dataframes.append(df)
#
# # Concatenate all DataFrames in the list into a single DataFrame
# df_rides = pd.concat(dataframes, ignore_index=True)
#
# # filters for all start and end coordinates to be within new york city boundary
# df_rides = df_rides[df_rides.apply(lambda row: is_valid_location(row['start_lat'], row['start_lng']), axis=1)]
# df_rides = df_rides[df_rides.apply(lambda row: is_valid_location(row['end_lat'], row['end_lng']), axis=1)]
#
# # create map of grid cells to their boundaries
# grid_cells = {}
#
# # Assign grid cells and their boundaries to each ride's origin location
# df_rides[['origin_grid_cell']] = df_rides.apply(
#     lambda row: pd.Series(get_grid_cell_with_center(
#         row['start_lat'], row['start_lng'], lat_min, lon_min, lat_step, lon_step, grid_cells
#     )), axis=1
# )
#
# # Assign grid cells and their boundaries to each ride's destination location
# df_rides[['destination_grid_cell']] = df_rides.apply(
#     lambda row: pd.Series(get_grid_cell_with_center(
#         row['end_lat'], row['end_lng'], lat_min, lon_min, lat_step, lon_step, grid_cells
#     )), axis=1
# )
#
# with open('grid_cells_2024.json', 'w') as file:
#     json.dump(grid_cells, file)

with open('grid_cells_2024.json', 'r') as file:
    grid_cells = json.load(file)
# df_rides.to_csv('df_rides_2024.csv', index=False)
df_rides = pd.read_csv('df_rides_2024.csv')

# Aggregate the total number of rides that ended in each grid cell
aggregated_destination_rides = df_rides.groupby('destination_grid_cell').size().reset_index(name='total_destination_rides')

# get the top n most visited destinations
n = 3
top_n_destinations = aggregated_destination_rides.sort_values(by='total_destination_rides', ascending=False).head(n)
# get number of rides within x distance away for origin

# max_bucket = []
# max_bucket_electric = []
for i in range(n):
    dest = top_n_destinations.iloc[i]
    dest_grid_cell = dest['destination_grid_cell']
    dest_center = grid_cells[dest_grid_cell]
    df_rides_filtered = df_rides[df_rides['destination_grid_cell'] == dest_grid_cell]
    df_rides_filtered['distance_to_top_destination'] = df_rides_filtered.apply(
        lambda row: calculate_distance(row['start_lat'], row['start_lng'], dest_center[0], dest_center[1]),
        axis=1
    )
    df_rides_filtered.to_csv('distance_to_top_' + str(i) + '_2024.csv')
    df_rides_electric = df_rides_filtered.copy(deep=True)
    df_rides_classic = df_rides_filtered.copy(deep=True)
    df_rides_electric = df_rides_electric.drop(df_rides_electric[df_rides_electric['rideable_type'] != "electric_bike"].index)
    df_rides_classic = df_rides_classic.drop(df_rides_classic[df_rides_classic['rideable_type'] != "classic_bike"].index)

    bins = range(0, 19000, 500)
    #df_rides_filtered['distance_bin'] = pd.cut(df_rides_filtered['distance_to_top_destination'], bins=bins)
    df_rides_electric['distance_bin'] = pd.cut(df_rides_electric['distance_to_top_destination'], bins=bins)
    df_rides_classic['distance_bin'] = pd.cut(df_rides_classic['distance_to_top_destination'], bins=bins)

    # Aggregate the number of rides for each distance bin
    #distance_ride_counts = df_rides_filtered.groupby('distance_bin').size().reset_index(name='num_rides')
    distance_ride_counts_classic = df_rides_classic.groupby('distance_bin').size().reset_index(name='num_rides')
    distance_ride_counts_electric = df_rides_electric.groupby('distance_bin').size().reset_index(name='num_rides')

    #normalize the number of rides based on bin
    # distance_ride_counts[['num_rides']] = distance_ride_counts.apply(
    #     lambda row: pd.Series(normalize(
    #         row['num_rides'], row['distance_bin'])), axis=1
    # )
    distance_ride_counts_classic[['num_rides']] = distance_ride_counts_classic.apply(
        lambda row: pd.Series(normalize(
            row['num_rides'], row['distance_bin'])), axis=1
    )
    distance_ride_counts_electric[['num_rides']] = distance_ride_counts_electric.apply(
        lambda row: pd.Series(normalize(
            row['num_rides'], row['distance_bin'])), axis=1
    )

    # get buckets where ridership peaks
    # idmax = distance_ride_counts['num_rides'].idxmax()
    # max_bucket.append(distance_ride_counts['distance_bin'].loc[idmax])

    plot_bins = [math.log10(x + 250) if x != 0 else math.log10(250) for x in bins]
    plot_bins = plot_bins[:-1]
    # distance_ride_counts.to_csv('top_' + str(i) + '_distance.csv', index=False)
    # distance_ride_counts_classic.to_csv('top_' + str(i) + '_distance_classic_2024.csv', index=False)
    # distance_ride_counts_electric.to_csv('top_' + str(i) + '_distance_electric_2024.csv', index=False)
    plt.figure(figsize=(10, 6))
    #plt.plot(plot_bins, distance_ride_counts['num_rides'], marker='o', label='classic')
    plt.plot(plot_bins, distance_ride_counts_classic['num_rides'], marker='o', label='classic')
    plt.plot(plot_bins, distance_ride_counts_electric['num_rides'], marker='o', label='electric')
    plt.xticks(rotation=90)
    plt.xlabel('Distance from Destination (meters)')
    plt.ylabel('Number of Rides')
    plt.title('Classic v Electric: Number of Rides vs Distance from Destination- ')
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    # plt.show()
    # plt.savefig('plot' + str(i) + '_classic_v_electric_2024.png')

# print(max_bucket)
# print(max_bucket_electric)
# TODO: Account for bounds of ocean in calculating normalizing area