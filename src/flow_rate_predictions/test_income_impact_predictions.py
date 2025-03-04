import math

import numpy as np
import torch
import csv
import torch.nn as nn
from sklearn.preprocessing import StandardScaler

# This file evaluates the performance of the model for predicting mobility flow rates based on income levels, pre & post Covid
# I used this file to experiment how changing features like number of jobs in a census tract effect overall mobility flow predictions

# load model
model = nn.Sequential(
    nn.Linear(15, 24),
    nn.ReLU(),
    nn.Linear(24, 12),
    nn.ReLU(),
    nn.Linear(12, 6),
    nn.ReLU(),
    nn.Linear(6, 1)
)
model.load_state_dict(torch.load('model_log.pt'))
model.eval()

scaler = StandardScaler()
# pre covid model
scaler.mean_ = np.array([4.97404925, 353.6761143, 557.01443929, 1228.44536973, 384.87819943, 627.60903125, 1047.90474451, 1136.12389869, 1589.84773001, 4834.607063,
  370.39652045, 527.9685566, 1240.16237506, 8.27161937, 12.44311739])
scaler.scale_ = np.array([3.96707610e+00, 1.06095061e+03, 1.22806123e+03, 4.37376530e+03,
 1.92432161e+02, 3.26526928e+02, 7.35926280e+02, 2.61542988e+03,
 2.69665707e+03, 1.02434943e+04, 2.07417513e+02, 3.26878742e+02,
 9.60200067e+02, 1.20272039e+01, 1.69269760e+01])
# post covid model
# scaler.mean_ = np.array([4.64453817,  307.42309632,  499.48516175,  975.94778343,  381.12318342,
#   622.35125078, 1014.22815141,  884.43035499, 1293.51159859, 3465.93059949,
#   364.29865982,  547.50799218, 1123.29565702,    7.99882333,   11.78266783])
# scaler.scale_ = np.array([4.12265094e+00, 8.38260097e+02, 1.04159751e+03, 3.50579066e+03,
#  1.89943062e+02, 3.18430138e+02, 6.94584204e+02, 2.27954932e+03,
#  2.40835449e+03 ,8.52402066e+03, 2.05845605e+02, 3.36190910e+02,
#  8.90874829e+02, 1.22009984e+01, 1.87586272e+01])

with torch.no_grad():
    # Test effect of income jobs on stuff
    # grab 20 random entries, increase destination high num jobs (work)

    # grab 20 random entries, decrease destination num jobs in general

    # select 10 lower socioeconomic geoids as destination, increase high num jobs (work) - 36005 -> the bronx
    y = []
    X = []
    low_income_flow_increase = []
    low_income_flow_increase.append(('geoid_o', 'percent_accuracy'))
    with open('/Users/emmacorbett/PycharmProjects/SUSE_Project/neural_network_model_data_hudson_yards_before_geoids.csv',
              mode='r') as file:
        csvFile = csv.reader(file)
        csvFile.__next__()
        for line in csvFile:
            #if '36005' in line[17]:
            if '36005006300' == line[17]:
                features = line[0:15]
                features = [float(x) for x in features]
                # increase number of high jobs in destination by 10%
                features[4] *= 1.1
                features[5] *= 1.1
                # features[4] *= 1.2
                # features[5] *= 1.2
                # features[8] *= 1.5
                # features[9] *= 1.5
                #features[14] *= 1.2

                X.append(features)
                flow = 0.0 if float(line[15]) == 0 else math.log2(float(line[15]))
                y.append((line[16], flow))

    X = np.array(X)

    num = 0
    for test in X:
        test = np.reshape(test, (1, 15))
        test_da = scaler.transform(test)
        test_da = torch.tensor(test_da, dtype=torch.float32)

        y_pred = model(test_da)
        y_pred = y_pred[0].numpy()
        y_act = y[num][1]
        # percent off
        percent_off = (y_act - y_pred) / y_pred if y_pred != 0 else y_act
        low_income_flow_increase.append((y[num][0], percent_off*-1))
        num += 1

    with open('bronx_increase_high_income_jobs.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        for tup in low_income_flow_increase:
            writer.writerow(tup)