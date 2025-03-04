import os
import pandas as pd
import re
import csv

# This file takes the mobility flow data and merges it into one file, where each row's origin and destination are in New York, NY

# Change these paths to your own data files
input_folder = "/Users/emmacorbett/PycharmProjects/SUSE_Project/weekly_flows/ct2ct/2021_06_28/"
output_path = "../data/little_island_data/ny_after_little_island_ct2ct_2021_06_28.csv"

# Merge all files
flow_all = []
flow_all.append(["geoid_o","geoid_d","lng_o","lat_o","lng_d","lat_d","date_range","visitor_flows","pop_flows"])
pattern = re.compile(r'^(36005|36061|36047|36081|36085)') # NYC Counties, 061 is new york county, 36 in NY state
for file in os.listdir(input_folder):
    if file[-3:] == "csv":
        with open("/Users/emmacorbett/PycharmProjects/SUSE_Project/weekly_flows/ct2ct/2021_06_28/" + file) as f:
            csvFile = csv.reader(f)
            for lines in csvFile:
                if pattern.match(str(lines[0])) and pattern.match(str(lines[1])): # checks that all origin and destinations are within New York, NY
                    flow_all.append(lines)

flow_all = pd.DataFrame(flow_all)
flow_all.to_csv(output_path, index=False, header=False)