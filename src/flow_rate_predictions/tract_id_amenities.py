import numpy as np, pandas as pd, matplotlib.pyplot as plt
import geopandas as gpd
import math

'''
This file compares the flow rates from different census tracts to hudson yards before the opening of hudson yards and after. 
It then compares the actual change in flow rates to the predicted flow rates from the machine learning model. 
It then specifically looks at a case study of census tracts in the bronx and plots those. Results shown in the README.md file
'''
# shapefiles
census_tracts = gpd.read_file('/Users/emmacorbett/PycharmProjects/CIEN4012/nyct2020.shp')
census_tracts.head()

#attraction_zone = gpd.read_file('Hudson_Yards_Cut.shp')

fig, ax = plt.subplots()
census_tracts.plot(ax=ax)
#attraction_zone.plot(ax=ax, color='red', alpha=0.7)

h_flow = pd.read_csv('/Users/emmacorbett/PycharmProjects/SUSE_Project/data/hudson_yards_data/destination_hudson_yards_before_2019_04_29.csv')
geoid_flow_map = {}
for index, row in h_flow.iterrows():
    geoid_flow_map[str(row['geoid_o'])] = row['pop_flows']

census_tracts['flow_before'] = np.NaN
for i in range(len(census_tracts)):
    flow = 0
    if census_tracts['GEOID'][i] in geoid_flow_map:
        if geoid_flow_map[census_tracts['GEOID'][i]] > 0:
            flow = math.log2(geoid_flow_map[census_tracts['GEOID'][i]])
    census_tracts['flow_before'][i] = flow

census_tracts.plot('flow_before', legend=True)

h_flow_after = pd.read_csv('/Users/emmacorbett/PycharmProjects/SUSE_Project/data/hudson_yards_data/destination_hudson_yards_after_2019_07_08.csv')
geoid_flow_map_after = {}
for index, row in h_flow_after.iterrows():
    geoid_flow_map_after[str(row['geoid_o'])] = row['pop_flows']

census_tracts['flow_after'] = np.NaN
for i in range(len(census_tracts)):
    flow = 0
    if census_tracts['GEOID'][i] in geoid_flow_map_after:
        if geoid_flow_map_after[census_tracts['GEOID'][i]] > 0:
            flow = math.log2(geoid_flow_map_after[census_tracts['GEOID'][i]])
    census_tracts['flow_after'][i] = flow

census_tracts.plot('flow_after', legend=True)

census_tracts['flow_change'] = np.NaN
# for i in range(len(census_tracts)):
#     if census_tracts['GEOID'][i] in geoid_flow_map_after and census_tracts['GEOID'][i] in geoid_flow_map:
#         flow_before = census_tracts['flow_before'][i]
#         flow_after = census_tracts['flow_after'][i]

#         change = flow_after - flow_before
#         percent = 0
#         if flow_before == 0 and change != 0:
#             percent = 1
#         elif flow_before != 0:
#             percent = change/flow_before

#         census_tracts['flow_change'][i] = percent

for i in range(len(census_tracts)):
    if census_tracts['GEOID'][i] in geoid_flow_map_after and census_tracts['GEOID'][i] in geoid_flow_map:
        flow_before = census_tracts['flow_before'][i]
        flow_after = census_tracts['flow_after'][i]

        change = (flow_after - flow_before) * -1
        percent = 0
        if flow_before == 0 and change != 0:
            percent = 1
        elif flow_before != 0:
            percent = change / flow_before

        census_tracts['flow_change'][i] = percent

census_tracts.plot('flow_change', legend=True, cmap='RdBu')

census_tracts['predictions'] = np.NaN

h_flow_predictions = pd.read_csv('/Users/emmacorbett/PycharmProjects/SUSE_Project/code/hy_after_predictions.csv')
geoid_prediction_after = {}
for index, row in h_flow_predictions.iterrows():
    geoid_prediction_after[str(row['geoid_o'])] = row['percent_accuracy']

for i in range(len(census_tracts)):
    if census_tracts['GEOID'][i] in geoid_flow_map_after and census_tracts['GEOID'][i] in geoid_flow_map and \
            census_tracts['GEOID'][i] in geoid_prediction_after:
        census_tracts['predictions'][i] = geoid_prediction_after[census_tracts['GEOID'][i]]

census_tracts.plot('predictions', legend=True, cmap='RdBu')

census_tracts['bronx_predictions'] = np.NaN

b_flow_predictions = pd.read_csv(
    '/Users/emmacorbett/PycharmProjects/SUSE_Project/code/bronx_increase_high_income_jobs.csv')
geoid_prediction_bronx = {}
for index, row in b_flow_predictions.iterrows():
    geoid_prediction_bronx[str(row['geoid_o'])] = row['percent_accuracy']

for i in range(len(census_tracts)):
    geoid = census_tracts['GEOID'][i]
    if geoid in geoid_prediction_bronx:
        census_tracts['bronx_predictions'][i] = geoid_prediction_bronx[geoid]

census_tracts.plot('bronx_predictions', cmap='RdBu')