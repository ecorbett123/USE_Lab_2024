# USE_Lab
Urban Systems Engineering Lab, Summer 2024

This project was motivated largely by my belief in the importance of providing affordable and equitable public transportation.
Transportation is an essential way to connect communities and combat inequality and provide equal access to jobs and community resources.
With that in mind, I carried out three different projects centered around studying mobility patterns in New York City to further my understanding of areas of improvement in our current transportation network. 

## Contents:
This repository contains three main directories. Each directory has their own ReadMe describing the research goal. 
1. Agent_based_model: focus on bike networks and the urban heat island effect (how cities are getting hotter due to climate change and how that disproportionately effects different communities)
2. Flow_rate_predictions: using neural networks to predict mobility patterns, comparing pre- and post-Covid trends as well as pre- and post-opening of points of interest such as Hudson Yards
3. Universal_visitation_law_analysis: studying if current biking data in NYC supports the universal visitation law so that we can use the law as a baseline for further predictions


## Technologies Used:
- Open Street Map (OSM), geospatial data
- Networkx, graph theory
- Machine learning, neural networks 
- Agent based modelling techniques 
- Urban engineering algorithms 

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