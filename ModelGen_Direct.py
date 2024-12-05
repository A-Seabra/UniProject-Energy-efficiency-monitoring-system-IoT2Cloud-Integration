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


# Set up Adafruit IO client
ADAFRUIT_IO_USERNAME = ''
ADAFRUIT_IO_KEY = ''
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
#-----------------------------------------------------------------------------------------------------------------

#Replace YOUR_USERNAME and YOUR_KEY with your Adafruit IO username and API key
url = 'https://io.adafruit.com/api/v2/ArturSeabra/feeds/temperatura/data.csv?limit=1000'
headers = {'X-AIO-Key': ''}
#Make a GET request to the Adafruit IO API
response = requests.get(url, headers=headers)


#Check if the response was successful
if response.status_code == 200:
    #Parse the CSV data using pandas
    data = pd.read_csv(io.StringIO(response.text))
    
    #Filter out rows with non-numeric values in the 'value' column
    data = data[pd.to_numeric(data['value'], errors='coerce').notnull()]
    
else:
    print('Error:', response.status_code)

data = data.drop('id', axis=1)
data = data.drop('feed_id', axis=1)
data = data.drop('lat', axis=1)
data = data.drop('lon', axis=1)
data = data.drop('ele', axis=1)
data = data.drop('created_epoch', axis=1)
data = data.drop('expiration', axis=1)
data = data.drop('feed_key', axis=1)

# Sort the data in ascending order based on the 'created_at' column
data = data.sort_values('created_at', ascending=True)

#-----------------------------------------------------------------------------------------------------------------
#Replace YOUR_USERNAME and YOUR_KEY with your Adafruit IO username and API key
url = 'https://io.adafruit.com/api/v2/ArturSeabra/feeds/niveldeluz/data.csv?limit=1000'
headers = {'X-AIO-Key': ''}
#Make a GET request to the Adafruit IO API
response = requests.get(url, headers=headers)


#Check if the response was successful
if response.status_code == 200:
    #Parse the CSV data using pandas
    data2 = pd.read_csv(io.StringIO(response.text))
    #print(data)
    #Filter out rows with non-numeric values in the 'value' column
    data2 = data2[pd.to_numeric(data2['value'], errors='coerce').notnull()]
    
else:
    print('Error:', response.status_code)

data2 = data2.drop('id', axis=1)
data2 = data2.drop('feed_id', axis=1)
data2 = data2.drop('lat', axis=1)
data2 = data2.drop('lon', axis=1)
data2 = data2.drop('ele', axis=1)
data2 = data2.drop('created_epoch', axis=1)
data2 = data2.drop('expiration', axis=1)
data2 = data2.drop('feed_key', axis=1)

# Sort the data in ascending order based on the 'created_at' column
data2 = data2.sort_values('created_at', ascending=True)
#-----------------------------------------------------------------------------------------------------------------

Data_merged = pd.merge(data, data2, on='created_at', how='inner')

Data_merged['created_at'] = pd.to_datetime(Data_merged['created_at'])
Data_merged = Data_merged.sort_values('created_at')
Data_merged['Luz_one_hour_prior'] = Data_merged['value_y'].shift(-1)
Data_merged = Data_merged.dropna()


# create a new column with the epoch timestamp
Data_merged['timestamp'] = Data_merged['created_at'].apply(lambda x: x.timestamp())

X = Data_merged[['timestamp','Luz_one_hour_prior']]  # predictor variable
y = Data_merged['value_x']  # target variable
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