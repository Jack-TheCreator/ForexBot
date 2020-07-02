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

    def __init__(self, key=None):
        if(key == None):
            pass
        else:
            redis = Redis()
            handler = Handler(redis)
            self.scaler = MinMaxScaler()
            self.data = handler.load_all(key)
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

    def loadModel(self,currentKey):
        path = currentKey + ".h5"
        self.model = models.load_model(path)

    def getPredictions(self, stickList):
        values = []
        for val in stickList:
            values.append(val['close'])

        values = np.asarray(values)

        # --------Predictions------------#
        values = values.reshape(-1)
        predictions = values[-self.time_steps:]
        for derp in range(self.predictAhead):
            x = predictions[-self.time_steps:]
            x = x.reshape((1, self.time_steps, 1))
            out = self.model.predict(x)[0][0]
            predictions = np.append(predictions, out)
        predictions = predictions[self.time_steps:]
        # --------------------------------#
        predictions = np.asarray(predictions)
        self.pred = np.reshape(predictions, (-1, 1))
        return(self.scaler.inverse_transform(self.pred))


    def buildModel(self, currentKey):


        trainSize = 0.8
        nuerons = [10, 15, 20 ,25]
        num_epochs = [100, 250, 500, 1000]
        reps = 5
        #self.time_steps

        time = self.data['relative_minute']
        close = self.data['close'].values
        trainSplit = int(len(self.data) * trainSize)
        train, test = close[:trainSplit], close[trainSplit:]
        train = np.reshape(train, (-1,1))
        test = np.reshape(test, (-1,1))

        trainData = TimeseriesGenerator(train, train, length=self.time_steps, batch_size=20)
        testData = TimeseriesGenerator(test, test, length=self.time_steps, batch_size=1)

        results = {}


        testVals = self.scaler.inverse_transform(test[self.time_steps:])
        for _ in range(reps):

            for n in nuerons:

                for e in num_epochs:
                    #######init Model##########
                    model = Sequential()
                    model.add(
                        LSTM(n,
                             activation='relu',
                             input_shape=(self.time_steps, 1))
                    )
                    model.add(Dense(1))
                    model.compile(optimizer='adam', loss='mse')
                    model.fit(trainData, epochs=e, verbose=1)
                    ###########################

                    pred = model.predict_generator(testData)
                    squared = []
                    for p, t in zip(pred, testVals):
                        squared.append((t - p) ** 2)
                    mean = sum(squared) / len(squared)

                    results[mean[0]] = model

        bestModel = results[min(results.keys())]

        path = currentKey + ".h5"
        bestModel.save(path)




