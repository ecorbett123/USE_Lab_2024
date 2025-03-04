import csv
import math

import matplotlib.pyplot as plt
import numpy as np

flow_rates_log = []
flow_rates = []
with open('/Users/emmacorbett/PycharmProjects/SUSE_Project/neural_network_model_data_2-march2020.csv', mode ='r') as file:
    csvFile = csv.reader(file)
    csvFile.__next__()
    for line in csvFile:
        flow = float(line[13])
        flow_rates.append(flow)
        if flow == 0:
            flow_rates_log.append(0.0)
        else:
            flow_rates_log.append(math.log2(flow))


counts, bins = np.histogram(flow_rates_log)
plt.ylabel("Log Flow Rate")
plt.stairs(counts, bins)
plt.show()