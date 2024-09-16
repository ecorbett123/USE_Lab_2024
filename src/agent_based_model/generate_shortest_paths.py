
import os
import pandas as pd
from datetime import datetime
import osmnx as ox

G = ox.load_graphml(filepath="/Users/emmacorbett/PycharmProjects/USE_Lab/src/agent_based_model/ny_bike_graph_heat_included_2.graphml")
dir_name = "/Users/emmacorbett/PycharmProjects/USE_Lab/data/Citibike/5_May_2024"

# Generate csv with shortest paths routes travelled over 5 times
dirs = os.listdir(dir_name) # dir_name should be the dir with all the raw citibike csv files
dataframes = []
for file in dirs:
    if file.endswith('.csv'):
        df_unfiltered = pd.read_csv(dir_name + "/" + file)
        dataframes.append(df_unfiltered)

combined_df = pd.concat(dataframes, ignore_index=True)
combined_df['started_at'] = pd.to_datetime(combined_df['started_at'])
combined_df['ended_at'] = pd.to_datetime(combined_df['ended_at'])
combined_df = combined_df[(combined_df['started_at'].dt.hour >= 11) & (combined_df['started_at'].dt.hour < 14) & (combined_df['end_lng']) & (combined_df['start_lng'])]

start_date = datetime.strptime('2024-05-01', '%Y-%m-%d').date()
end_date = datetime.strptime('2024-05-08', '%Y-%m-%d').date()

# fileter to midday for the first week of the month
df = combined_df[(combined_df['started_at'].dt.date >= start_date) & (combined_df['started_at'].dt.date < end_date)]

# save map of station ids to lat/lng values
lat_lng_map = {}
for _, row in df.iterrows():
    lat_lng_map[row['start_station_id']] = (row['start_lat'], row['start_lng'])
    lat_lng_map[row['end_station_id']] = (row['end_lat'], row['end_lng'])
df = df[['start_station_id', 'end_station_id']]

# Group by origin and destination, then count the number of trips
od_counts = df.groupby(['start_station_id', 'end_station_id']).size().reset_index(name='trip_count')

# Create an origin-destination matrix
od_matrix = od_counts.pivot(index='start_station_id', columns='end_station_id', values='trip_count')

# Fill NaN values with 0 (indicating no trips between those stations)
od_matrix = od_matrix.fillna(0)
od_matrix = od_matrix.stack().reset_index()
od_matrix.columns = ['origin', 'destination', 'trip_count']

# Sort the DataFrame by trip count in descending order
od_flat_sorted = od_matrix.sort_values(by='trip_count', ascending=False)
od_flat_sorted = od_flat_sorted[od_flat_sorted['trip_count'] > 5.0]

# Append shortest route entries
routes = []
origs = []
for _, row in od_flat_sorted.iterrows():
    start_lng = lat_lng_map[row['origin']][1]
    start_lat = lat_lng_map[row['origin']][0]
    end_lng = lat_lng_map[row['destination']][1]
    end_lat = lat_lng_map[row['destination']][0]
    # code to calculate and save shortest path information on first run
    orig = ox.distance.nearest_nodes(G, X=start_lng, Y=start_lat)
    dest = ox.distance.nearest_nodes(G, X=end_lng, Y=end_lat)
    route = ox.shortest_path(G, orig, dest, weight="travel_time")
    origs.append(orig)
    routes.append(route)
od_flat_sorted['shortest_path'] = routes
od_flat_sorted['origin_osm_node'] = origs
# save final csv for the od pairs, number riders, and shortest path calculated
# 95566 unique od pairs in total with at least one trip for may 2024 data
# 1548 unique od pairs with greater than 5 trips for may 2024 data
od_flat_sorted.to_csv('top_journey_counts.csv', index=False)