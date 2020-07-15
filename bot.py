import websocket
import orjson
import json
from dateutil.parser import parse
from datetime import datetime
from threading import Thread
#from candle import stick
import os
from DBHandler import Handler
from redis import Redis
import threading
import modeling
import matplotlib.pyplot as plt
import seaborn as sb
from matplotlib import style
style.use("ggplot")

class ForexBot():
    def __init__(self, crypto=False):
        self.redis = Redis()
        self.handler = Handler(self.redis)
        self.predicter = modeling.Modeling()
        self.currentMin = -1
        self.relative_minute = 0
        self.currentHour = -1
        self.stickList = []
        self.currentKey = ""
        self.crypto = crypto

        self.markets = {"AUS": ["C.NZD/USD", "C.USD/AUD"],
                   "ASI": ["C.AUD/JPY", "C.AUD/HKD"],
                   "EUR": ['C.JPY/EUR', 'C.HKD/GBP'],
                   "USA": ['C.EUR/USD', 'C.GBP/USD'],
                   "CRYPTO": ["XT.BTC-USD"]}

    def getModel(self):
        self.predicter.loadModel(self.currentKey)

    def Onopen(self):

        print('OPEN++++++')
        auth = {
            "action": "auth",
            "params": os.environ.get("API_KEY")

        }
        self.ws.send(json.dumps(auth))
        self.ws.send(json.dumps({"action": "subscribe", "params": self.keys[0]}))

    def buildModel(self):
        builder = modeling.Modeling(self.currentKey)
        builder.buildModel(self.currentKey)

    def newHour(self):

        time = datetime.now().hour

        if (time in [3, 8, 17, 19]):
            # Market Change
            # Save Current market, Unsub, Sub new market
            # Eventually use model trained on yesterdays data
            # REÉËĘ
            print(self.handler.save_minutes(self.stickList[:-1], self.currentKey))
            t1 = threading.Thread(target=self.buildModel, name="t1")
            t1.start()
            self.stickList = []
            self.relative_minute = 0
            self.currentMin = -1
            self.ws.send(json.dumps({"action": "unsubscribe", "params": self.markets[self.currentKey][0]}))
            self.keys = self.getActiveMarkets()

            self.ws.send(json.dumps({"action": "subscribe", "params": self.keys[0]}))



    def Graph(self):
        dx = []
        dy = []
        predx = []
        predy = []

        for data in self.stickList[-15:]:
            dx.append(data['close'])
            dy.append(data['relative_minute'])

        endMin = self.stickList[-1]['relative_minute']

        for data in self.pred:
            predx.append(data)
            endMin += 1
            predy.append(endMin)
        print('l')
        plt.figure(figsize=(15, 10))
        sb.lineplot(dx, dy, label='data')
        sb.lineplot(predx, predy, label='predictions')
        plt.xticks(fontsize=16)
        plt.xlabel("Price", fontsize=15)
        plt.ylabel("Relative Minute", fontsize=15)
        plt.yticks(fontsize=16)
        plt.show()


    def on_message(self, message):
        msg = orjson.loads(message)[0]
        if (msg['ev'] == 'status'):
            pass
        else:

            if (self.crypto):
                bid = msg['p']
            else:
                ask = msg['a']
                bid = msg['b']
            dt_obj = datetime.fromtimestamp(msg['t'] / 1000.0)

            if (self.currentMin == dt_obj.minute):
                if (bid < self.stickList[-1]['low']):
                    self.stickList[-1]['low'] = bid
                elif (bid > self.stickList[-1]['high']):
                    self.stickList[-1]['high'] = bid
            elif (self.currentMin == -1):
                self.currentMin = dt_obj.minute
                self.currentHour = dt_obj.hour
                self.stickList.append(
                    {'high': bid, 'low': bid, 'open': bid, 'minute': self.currentMin, 'relative_minute': self.relative_minute})
            else:
                self.relative_minute = self.relative_minute + 1
                print(self.relative_minute)
                self.stickList[-1]['close'] = bid
                self.currentMin = dt_obj.minute
                self.stickList.append(
                    {'high': bid, 'low': bid, 'open': bid, 'minute': self.currentMin, 'relative_minute': self.relative_minute})

                # trend = ['nuetral', 0]
                # if(len(stickList)>3):
                #     if((stickList[-2]['close']<stickList[-3]['close'])and(stickList[-3]['close']<stickList[-4]['close'])):
                #         print('trending down')
                #         trend[0] = 'down'
                #         trend[1] = trend[1] - 1
                #     elif((stickList[-2]['close']>stickList[-3]['close'])and(stickList[-3]['close']>stickList[-4]['close'])):
                #         print('trending up')
                #         trend[0] = 'Up'
                #         if(trend[1]< -3):
                #             print('buying')
                #             print('buy at', bid, 'sell at', (bid - (bid-stickList[-4]['close'])) + bid, 'for', (bid - (bid-stickList[-4]['close'])))
                #         else:
                #             trend[1] = 0
                if (len(self.stickList) > 15):
                    self.preds = self.predicter.getPredictions(self.stickList[:-1])
                    t2 = threading.Thread(target=self.Graph, name="t2")
                    t2.start()

                if (self.currentHour != dt_obj.hour):
                    self.currentHour = dt_obj.hour
                    print('newHour')
                    self.newHour()

    def Onclose(self):
        print('closed')
        self.keys = self.getActiveMarkets()
        if (self.crypto):
            address = 'wss://socket.polygon.io/crypto'
        else:
            address = 'wss://socket.polygon.io/forex'
        self.ws = websocket.WebSocketApp(address, on_open=self.Onopen, on_close=self.Onclose, on_message=self.on_message)
        self.ws.run_forever()

    def getActiveMarkets(self):

        time = datetime.now().hour
        if (self.crypto):
            return (self.markets["CRYPTO"])
        if (time >= 17 and time < 19):
            self.currentKey = "AUS"
            return (self.markets["AUS"])
        if ((time >= 19) or (time < 3)):
            self.currentKey = "ASI"
            return (self.markets["ASI"])
        if (time >= 3 and time < 8):
            self.currentKey = "EUR"
            return (self.markets["EUR"])
        if (time >= 8 and time < 17):
            self.currentKey = "USA"
            return (self.markets["USA"])

    def runBot(self):
        self.keys = self.getActiveMarkets()
        if(self.crypto):
            address = 'wss://socket.polygon.io/crypto'
        else:
            address = 'wss://socket.polygon.io/forex'

        print('yo')

        self.ws = websocket.WebSocketApp(address, on_open=self.Onopen, on_close=self.Onclose, on_message=self.on_message)
        self.ws.run_forever()


testBot = ForexBot()
testBot.runBot()