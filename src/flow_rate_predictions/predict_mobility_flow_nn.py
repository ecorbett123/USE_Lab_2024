import copy
import math

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import tqdm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import csv

# This file creates a neural network to predict mobility flow rates from different census tracts to hudson yards pre-Covid.

y = []
X = []
with open('/Users/emmacorbett/PycharmProjects/SUSE_Project/neural_network_model_data_2-march2020.csv', mode ='r') as file:
    csvFile = csv.reader(file)
    csvFile.__next__()
    for line in csvFile:
        features = line[0:13]
        features.append(line[14])
        features.append(line[15])
        features = [float(x) for x in features]
        X.append(features)
        flow = 0.0 if float(line[13]) == 0 else math.log2(float(line[13]))
        y.append(flow)

y = np.array(y)
X = np.array(X)

# train-test split for model evaluation
X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, train_size=0.7, shuffle=True)

# Standardizing data
scaler = StandardScaler()
scaler.fit(X_train_raw)
X_train = scaler.transform(X_train_raw)
X_test = scaler.transform(X_test_raw)

# Convert to 2D PyTorch tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32).reshape(-1, 1)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32).reshape(-1, 1)

# Define the model
model = nn.Sequential(
    nn.Linear(15, 24),
    nn.ReLU(),
    nn.Linear(24, 12),
    nn.ReLU(),
    nn.Linear(12, 6),
    nn.ReLU(),
    nn.Linear(6, 1)
)

# loss function and optimizer
loss_fn = nn.MSELoss()  # mean square error
optimizer = optim.Adam(model.parameters(), lr=0.0001)

n_epochs = 100  # number of epochs to run
batch_size = 10  # size of each batch
batch_start = torch.arange(0, len(X_train), batch_size)

# Hold the best model
best_mse = np.inf  # init to infinity
best_weights = None
history = []

for epoch in range(n_epochs):
    model.train()
    with tqdm.tqdm(batch_start, unit="batch", mininterval=0, disable=True) as bar:
        bar.set_description(f"Epoch {epoch}")
        for start in bar:
            # take a batch
            X_batch = X_train[start:start + batch_size]
            y_batch = y_train[start:start + batch_size]
            # forward pass
            y_pred = model(X_batch)
            loss = loss_fn(y_pred, y_batch)
            # backward pass
            optimizer.zero_grad()
            loss.backward()
            # update weights
            optimizer.step()
            # print progress
            bar.set_postfix(mse=float(loss))
    # evaluate accuracy at end of each epoch
    model.eval()
    y_pred = model(X_test)
    mse = loss_fn(y_pred, y_test)
    mse = float(mse)
    history.append(mse)
    if mse < best_mse:
        best_mse = mse
        best_weights = copy.deepcopy(model.state_dict())

# restore model and return best accuracy
model.load_state_dict(best_weights)
print("RMSE: %.2f" % np.sqrt(best_mse))
plt.xlabel("Number Training Iterations")
plt.ylabel("RMSE")
plt.title("Pre Covid RMSE Graph")
plt.plot(history)
plt.show()

model.eval()

torch.save(model.state_dict(), './model_log_post_covid.pt') # save the model

f = open("scaler_post_covid.txt", "a")
f.write(str(scaler.mean_) + "\n")
f.write(str(scaler.scale_))
f.close()