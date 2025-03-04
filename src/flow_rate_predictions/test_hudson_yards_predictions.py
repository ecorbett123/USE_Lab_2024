import math

import numpy as np
import torch
import csv
import torch.nn as nn
from sklearn.preprocessing import StandardScaler

# This file evaluates the performance of the model for predicting mobility flow rates to Hudson Yard pre & post the opening of Hudson Yards

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
scaler.mean_ = np.array([4.97404925, 353.6761143, 557.01443929, 1228.44536973, 384.87819943, 627.60903125, 1047.90474451, 1136.12389869, 1589.84773001, 4834.607063,
  370.39652045, 527.9685566, 1240.16237506, 8.27161937, 12.44311739])
scaler.scale_ = np.array([3.96707610e+00, 1.06095061e+03, 1.22806123e+03, 4.37376530e+03,
 1.92432161e+02, 3.26526928e+02, 7.35926280e+02, 2.61542988e+03,
 2.69665707e+03, 1.02434943e+04, 2.07417513e+02, 3.26878742e+02,
 9.60200067e+02, 1.20272039e+01, 1.69269760e+01])

with torch.no_grad():
    # Test accuracy of predictions from after hudson yards data
    hudson_yards_after_predictions = []
    hudson_yards_after_predictions.append(('geoid_o', 'percent_accuracy'))
    test_hy_data = []
    test_hy_data_results = []
    with open('/Users/emmacorbett/PycharmProjects/SUSE_Project/neural_network_model_data_hudson_yards_after_geoids.csv', mode='r') as file2:
        csvFile = csv.reader(file2)
        csvFile.__next__()
        for line in csvFile:
            x_sample = line[0:15]
            x_sample = [float(x) for x in x_sample]
            test_hy_data.append(x_sample)
            flow = 0.0 if float(line[15]) == 0 else math.log2(float(line[15]))
            test_hy_data_results.append((line[16], flow))

    test_hy_data = np.array(test_hy_data)
    num = 0
    for test_d in test_hy_data:
        test_d = np.reshape(test_d, (1, 15))
        test_da = scaler.transform(test_d)
        test_da = torch.tensor(test_da, dtype=torch.float32)

        y_pred = model(test_da)
        y_pred = y_pred[0].numpy()
        y_act = test_hy_data_results[num][1]
        # percent off
        percent_off = (y_act - y_pred)/y_pred if y_pred != 0 else y_act
        hudson_yards_after_predictions.append((test_hy_data_results[num][0], percent_off))
        num += 1

    with open('hy_after_predictions_notlog.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        for tup in hudson_yards_after_predictions:
            writer.writerow(tup)