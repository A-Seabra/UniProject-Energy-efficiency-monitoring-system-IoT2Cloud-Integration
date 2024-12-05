import requests
import numpy as np
from joblib import dump, load
import datetime
from Adafruit_IO import Client, Feed
import time
import warnings

warnings.filterwarnings("ignore")



# Set up Adafruit IO client
ADAFRUIT_IO_USERNAME = 'ArturSeabra'
ADAFRUIT_IO_KEY = ''
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Create a feed on Adafruit IO
FEED_NAME = 'previsao-de-temperatura'
try:
    feed = aio.feeds(FEED_NAME)
except:
    feed = Feed(name=FEED_NAME)
    feed = aio.create_feed(feed)


def print_with_timestamp(*args, **kwargs):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ", end="")
    print(*args, **kwargs)


while True:

    model = load('LR_model.joblib')

    #-------------------------------------------------------------------------------------  Obter valor de Luz mais recente
    url = 'https://io.adafruit.com/api/v2/ArturSeabra/feeds/niveldeluz/data/last'
    headers = {'X-AIO-Key': ''}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        luz_in = response.json()
        luz_val = luz_in['value']
        luz = float(luz_val)
        print_with_timestamp('Most recent Luz value:', luz)
    else:
        print_with_timestamp('Error:', response.status_code)

    #-------------------------------------------------------------------------------------  Obter data de aqui a uma hora
    now = datetime.datetime.now()
    future_time = now + datetime.timedelta(hours=1)
    future_timestamp = future_time.timestamp()

    #-------------------------------------------------------------------------------------  Obter a previsao
    new_y_pred = model.predict([[future_timestamp, luz]])
    arr = np.array(new_y_pred)
    valor_previsto = arr.item()

    #-------------------------------------------------------------------------------------  Enviar para o adafruit
    aio.send_data(feed.key, valor_previsto)
    print_with_timestamp('Prediction sent')
    time.sleep(20)
