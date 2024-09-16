# USE_Lab
Urban Systems Engineering Lab

Steps for generating heat map:
1. Run the write_data_from_wrf_to_csv.py file on the wrf files from the model to generate 3 files- lat, lon, and t2 values - these are matrices where each index corresponds to the same entry for each file; make sure to supply the file correct file paths
2. Run the create_osm_heat_bike_graph.py to create the osm graph with a heat value assigned to each node; make sure to supply the correct file paths 