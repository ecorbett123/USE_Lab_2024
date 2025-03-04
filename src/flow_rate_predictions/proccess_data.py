import geopy.distance
import pandas as pd
import geojson
import censusgeocode as cg

# This file aggregates work and resident attribute data for census tracts with mobility data
# Specifically, output file has a row with all features for model training, with y variable (total flow between that origin, destination) at the end of the row
# Current features include: 'distance_between_o_d', 'low_income_w_o', 'mid_income_w_o', 'high_income_w_o', 'low_income_r_o', 'mid_income_r_o', 'high_income_r_o', 'low_income_w_d', 'mid_income_w_d', 'high_income_w_d', 'low_income_r_d', 'mid_income_r_d', 'high_income_r_d', 'num_amenities_o', 'num_amenities_d'
# Feature selection based on paper "Quantifying the uncertainty of mobility flow predictions using Gaussian processes"
# This takes a whlie to run (2-4 hrs) but only need to run it once for data set

def get_num_amenities_by_census_tract():
    # uncomment this code and comment out the file code on first run to generate the file
    # tractid_num_amentities = {}
    # with open("/Users/emmacorbett/PycharmProjects/SUSE_Project/data/NY_POI.geojson") as f:
    #     gj = geojson.load(f)
    # for feature in gj['features']:
    #     location = feature['geometry']['coordinates']
    #     result = cg.coordinates(x=location[0], y=location[1])
    #     tract_id = result['Census Tracts'][0]['STATE'] + result['Census Tracts'][0]['COUNTY'] + result['Census Tracts'][0]['TRACT']
    #     num_amen = 0 if tract_id not in tractid_num_amentities else tractid_num_amentities[tract_id]
    #     tractid_num_amentities[tract_id] = num_amen + 1

    tractid_num_amentities = {}
    input_file = "/Users/emmacorbett/PycharmProjects/SUSE_Project/code/census_tract_amenities/census_tract_amenities_map_final.txt"
    with open(input_file) as f:
        for line in f.readlines():
            map = eval(line)
            for k, v in map.items():
                if k not in tractid_num_amentities:
                    tractid_num_amentities[k] = v
                else:
                    tractid_num_amentities[k] += v
    return tractid_num_amentities

def get_wattributes_map(w_attrs):
    # put work attributes into map
    geocode_wattributes_total_map = {}
    for index, row in w_attrs.iterrows():
        geocode = str(row['w_geocode'])[:11]
        geocode = int(geocode) # get first 11 nums for geocode to match flow code
        low_income = row['CE01']
        mid_income = row['CE02']
        high_income = row['CE03']
        if geocode not in geocode_wattributes_total_map:
            geocode_wattributes_total_map[geocode] = [low_income, mid_income, high_income]
        else:
            job_array = geocode_wattributes_total_map[geocode]
            job_array[0] += low_income
            job_array[1] += mid_income
            job_array[2] += high_income
            geocode_wattributes_total_map[geocode] = job_array
    return geocode_wattributes_total_map

def get_rattributes_map(r_attrs):
    # put resident attributes into map (exact same as above but with r_attrs data)
    geocode_rattributes_total_map = {}
    for index, row in r_attrs.iterrows():
        geocode = str(row['h_geocode'])[:11]  # get first 11 nums for geocode to match flow code
        geocode = int(geocode)
        low_income = row['CE01']
        mid_income = row['CE02']
        high_income = row['CE03']
        if geocode not in geocode_rattributes_total_map:
            geocode_rattributes_total_map[geocode] = [low_income, mid_income, high_income]
        else:
            job_array = geocode_rattributes_total_map[geocode]
            job_array[0] += low_income
            job_array[1] += mid_income
            job_array[2] += high_income
            geocode_rattributes_total_map[geocode] = job_array
    return geocode_rattributes_total_map

if __name__ == "__main__":
    # import points from csv file
    # work and resident attributes description- https://lehd.ces.census.gov/data/
    w_attrs = pd.read_csv('/Users/emmacorbett/PycharmProjects/SUSE_Project/data/ny_wac_S000_JT00_2019.csv') # downloaded from https://lehd.ces.census.gov/data/lodes/LODES7/ny/wac/ for the year 2019
    r_attrs = pd.read_csv('/Users/emmacorbett/PycharmProjects/SUSE_Project/data/ny_rac_S000_JT00_2019.csv') # downloaded from https://lehd.ces.census.gov/data/lodes/LODES7/ny/rac/
    flow_data = pd.read_csv('/Users/emmacorbett/PycharmProjects/SUSE_Project/data/ny_all_counties_weekly_flows_ct2ct_2020_03_02.csv') # mobility data- see read me for command to download a sample file to test with

    # get work and resident attribute maps
    geocode_wattributes_total_map = get_wattributes_map(w_attrs)
    geocode_rattributes_total_map = get_rattributes_map(r_attrs)

    # get map with amenities
    tract_amenities_map = get_num_amenities_by_census_tract()

    # y-value should be flow rates
    num_missing = 0
    data = []
    headers = ['distance_between_o_d', 'low_income_w_o', 'mid_income_w_o', 'high_income_w_o', 'low_income_r_o', 'mid_income_r_o', 'high_income_r_o', 'low_income_w_d', 'mid_income_w_d', 'high_income_w_d', 'low_income_r_d', 'mid_income_r_d', 'high_income_r_d', 'num_amenities_o', 'num_amenities_d', 'flow_rate', 'geoid_o', 'geoid_d']
    data.append(headers)
    for index, row in flow_data.iterrows():
        row_geoid_o = row['geoid_o']
        row_geoid_d = row['geoid_d']

        # get distance between origin and destination
        row_lat_lng_o = (row['lat_o'], row['lng_o'])
        row_lat_lng_d = (row['lat_d'], row['lng_d'])
        # (lat, long) for points to measure distance
        distance = geopy.distance.geodesic(row_lat_lng_o, row_lat_lng_d).mi

        if row_geoid_o in geocode_rattributes_total_map and row_geoid_d in geocode_rattributes_total_map and row_geoid_o in geocode_wattributes_total_map and row_geoid_d in geocode_wattributes_total_map:
            r_data_o = geocode_rattributes_total_map[row_geoid_o]
            r_data_d = geocode_rattributes_total_map[row_geoid_d]
            w_data_o = geocode_wattributes_total_map[row_geoid_o]
            w_data_d = geocode_wattributes_total_map[row_geoid_d]
            data_row = [distance]
            data_row.extend(w_data_o)
            data_row.extend(r_data_o)
            data_row.extend(w_data_d)
            data_row.extend(r_data_d)

            # num amenities
            if str(row_geoid_o) in tract_amenities_map:
                data_row.append(tract_amenities_map[str(row_geoid_o)])
            else:
                data_row.append(-1) # -1 amenities appended if no amenties reported for that census tract

            if str(row_geoid_d) in tract_amenities_map:
                data_row.append(tract_amenities_map[str(row_geoid_d)])
            else:
                data_row.append(-1) # -1 amenities appended if no amenties reported for that census tract

            # flow rate - y var
            data_row.append(row['pop_flows'])
            data_row.append(row_geoid_o)
            data_row.append(row_geoid_d)
            data.append(data_row)
        else:
            num_missing += 1

    a = pd.DataFrame(data)
    a.to_csv("neural_network_model_data_2.csv", header=False, index=False)
    print("Num Missing is: ", num_missing) # reports if any census tracts in mobility data are not found in w/r attributes... number should be zero