from DBHandler import Handler
from redis import Redis
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.preprocessing.sequence import TimeseriesGenerator



def initData():
    redis = Redis()
    handler = Handler(redis)
    data = handler.load_all('test')
    return(pd.DataFrame(data))



def main():

    time_steps = 15
    batch = 10
    units = 10
    num_epochs = 25

    data = initData()
    scaler = MinMaxScaler()
    data[['close','high','low']] = scaler.fit_transform(data[['close', 'high', 'low']])

    time = data['relative_minute']
    price = data['close'].values
    price = np.reshape(price, (-1,1))
    #Split here
    trainData = TimeseriesGenerator(price, price, length=time_steps, batch_size=batch)

    #######init Model##########
    model = Sequential()
    model.add(
        LSTM(units,
             activation='relu',
             input_shape=(time_steps, 1))
    )
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(trainData, epochs=num_epochs, verbose=1)
    ###########################

    predictAhead = 5

    #--------Predictions------------#
    price = price.reshape(-1)
    predictions = price[-time_steps:]
    for derp in range(predictAhead):
        x = predictions[-time_steps:]
        x = x.reshape((1,time_steps,1))
        out = model.predict(x)[0][0]
        predictions = np.append(predictions, out)
    predictions = predictions[time_steps-1:]
    #--------------------------------#

    print(predictions)



main()

