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
from keras import models
from keras.preprocessing.sequence import TimeseriesGenerator



class Modeling():

    def __init__(self):
        redis = Redis()
        handler = Handler(redis)
        self.scaler = MinMaxScaler()
        self.data = handler.load_all('test')
        self.data = pd.DataFrame(self.data)
        self.data[['close']] = self.scaler.fit_transform(self.data[['close']])
        self.predictAhead = 5
        self.time_steps = 15

    def graph(self):
        priceList = self.data['close'].values
        priceList = np.append(priceList, self.pred)
        priceList = np.reshape(priceList, (-1, 1))
        priceList = self.scaler.inverse_transform(priceList)
        minList = self.data['relative_minute'].values
        for i in range(self.predictAhead):
            minList = np.append(minList, (minList[-1] + 1))
        # priceList = np.reshape(priceList, (-1,1))
        # minList = np.reshape(minList, (-1, 1))
        dfprice = priceList[:-5]
        dfmin = minList[:-5]
        predprice = priceList[-5:]
        predmin = minList[-5:]
        plt.plot(dfmin, dfprice)
        plt.plot(predmin, predprice)
        plt.show()

    def getPredictions(self):

        model = models.load_model('my_model.h5')

        price = self.data['close'].values

        # --------Predictions------------#
        price = price.reshape(-1)
        predictions = price[-self.time_steps:]
        for derp in range(self.predictAhead):
            x = predictions[-self.time_steps:]
            x = x.reshape((1, self.time_steps, 1))
            out = model.predict(x)[0][0]
            predictions = np.append(predictions, out)
        predictions = predictions[self.time_steps:]
        # --------------------------------#
        predictions = np.asarray(predictions)
        self.pred = np.reshape(predictions, (-1, 1))
        return(self.scaler.inverse_transform(self.pred))


    def buildModel(self):

        batch = 10
        units = 10
        num_epochs = 25

        time = self.data['relative_minute']
        price = self.data['close'].values
        price = np.reshape(price, (-1,1))
        #Split here
        trainData = TimeseriesGenerator(price, price, length=self.time_steps, batch_size=batch)

        #######init Model##########
        model = Sequential()
        model.add(
            LSTM(units,
                 activation='relu',
                 input_shape=(self.time_steps, 1))
        )
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        model.fit(trainData, epochs=num_epochs, verbose=1)
        ###########################

        model.save('my_model.h5')




