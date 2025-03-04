# USE_Lab
Urban Systems Engineering Lab, Summer 2024

## Contents:
This repository contains three main directories. Each directory has their own ReadMe describing the research goal. 
1. Agent_based_model
2. Flow_rate_predictions
3. Universal_visitation_law_analysis


## Technologies Used:
- Open Street Map (OSM), geospatial data
- Networkx, graph theory
- Machine learning, neural networks 
- Agent based modelling techniques 
- Urban engineering formulas 

## Coding Notes:

Steps for generating heat map:
1. Run the write_data_from_wrf_to_csv.py file on the wrf files from the model to generate 3 files- lat, lon, and t2 values - these are matrices where each index corresponds to the same entry for each file; make sure to supply the file correct file paths
2. Run the create_osm_heat_bike_graph.py to create the osm graph with a heat value assigned to each node; make sure to supply the correct file paths 

Steps for generating bike paths with shortest paths:
1. Go to Citibike and download the data for the month/week of interest- https://s3.amazonaws.com/tripdata/index.html
2. Use the osm graph generated in the steps above for line 7 in generate_shortest_paths.py, citibike data for line 8
3. Run generate_shortest_paths.py; this will take a long time to run

Steps to run agent model:
1. Run the run.py file