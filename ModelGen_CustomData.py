import requests
import io

import pandas as pd
import numpy as np
from joblib import dump, load


from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import datetime
from Adafruit_IO import Client
from Adafruit_IO import Client, Feed
import random
import time

import warnings
warnings.filterwarnings("ignore")

data_Luz = pd.read_csv('C:/Users/artur/Desktop/ML-DTSD/Luz.csv')

data_Luz = data_Luz.drop('id', axis=1)
data_Luz = data_Luz.drop('feed_id', axis=1)
data_Luz = data_Luz.drop('lat', axis=1)
data_Luz = data_Luz.drop('lon', axis=1)
data_Luz = data_Luz.drop('ele', axis=1)

data_Luz.rename(columns={'value': 'Luz'}, inplace=True)

data_temp = pd.read_csv('C:/Users/artur/Desktop/ML-DTSD/Temperatura.csv')

data_temp = data_temp.drop('id', axis=1)
data_temp = data_temp.drop('feed_id', axis=1)
data_temp = data_temp.drop('lat', axis=1)
data_temp = data_temp.drop('lon', axis=1)
data_temp = data_temp.drop('ele', axis=1)

Data = pd.merge(data_temp, data_Luz, on='created_at', how='inner')

Data['created_at'] = pd.to_datetime(Data['created_at'])
Data = Data.sort_values('created_at')
Data['Luz_one_hour_prior'] = Data['Luz'].shift(-1)
Data = Data.dropna()

Data['timestamp'] = Data['created_at'].apply(lambda x: x.timestamp())

X = Data[['timestamp','Luz_one_hour_prior']]  # predictor variable
y = Data['value']  # target variable
model = LinearRegression()
model.fit(X, y)

# predict the target variable using the model
y_pred = model.predict(X)

# calculate RMSE (root mean squared error)
rmse = mean_squared_error(y, y_pred, squared=False)
print('RMSE:', rmse)

# calculate R-squared (coefficient of determination)
r2 = r2_score(y, y_pred)
print('R-squared:', r2)

# calculate Mean Absolute Error (MAE)
mae = mean_absolute_error(y, y_pred)
print("Mean Absolute Error (MAE):", mae)

# calculate Explained Variance Score (EVS)
evs = explained_variance_score(y, y_pred)
print("Explained Variance Score (EVS):", evs)

dump(model, 'LR_model.joblib')
print('Model Updated !')
