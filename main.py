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

redis = Redis()
#m = modeling.Modeling()
handler = Handler(redis)
currentMin = -1
currentHour = -1
minstick = {}
stickList = []
currentKey = ""
trendNum = 3
crypto = True
markets = {"AUS":["C.NZD/USD","C.USD/AUD"],
           "ASI":["C.AUD/JPY","C.AUD/HKD"],
           "EUR":['C.JPY/EUR','C.HKD/GBP'],
           "USA":['C.EUR/USD','C.GBP/USD'],
           "CRYPTO":["XT.BTC-USD"]}

relative_minute = 0

def getModel():
    #handler.save_minutes(stickList[:-1], 'test')
    print(m.getPredictions())

def Onopen(ws):
    global keys
    print('OPEN++++++')
    auth = {
        "action": "auth",
        "params": os.environ.get("API_KEY")

    }
    ws.send(json.dumps(auth))
    ws.send(json.dumps({"action":"subscribe","params":keys[0]}))

def newHour():
    global stickList, currentMin, relative_minute, currentKey
    time = datetime.now().hour

    if(time in [3,8,17,19]):
        #Market Change
        #Save Current market, Unsub, Sub new market
        #Eventually use model trained on yesterdays data
        #REÉËĘ
        handler.save_minutes(stickList[:-1], currentKey)
        stickList = []
        relative_minute = 0
        currentMin = -1
        ws.send(json.dumps({"action":"unsubscribe","params":markets[currentKey][0]}))
        keys = getActiveMarkets()
        ws.send(json.dumps({"action":"subscribe","params":keys[0]}))


def on_message(ws, message):
    global currentMin, minstick, relative_minute, currentHour
    msg = orjson.loads(message)[0]
    if(msg['ev']=='status'):
        pass
    else:

        if(crypto):
            bid = msg['p']
        else:
            ask = msg['a']
            bid = msg['b']
        dt_obj = datetime.fromtimestamp(msg['t']/1000.0)

        if(currentMin == dt_obj.minute):
            if(bid<stickList[-1]['low']):
                stickList[-1]['low'] = bid
            elif(bid>stickList[-1]['high']):
                stickList[-1]['high'] = bid
        elif(currentMin == -1):
            currentMin = dt_obj.minute
            currentHour = dt_obj.hour
            stickList.append({'high':bid, 'low':bid, 'open':bid, 'minute':currentMin, 'relative_minute': relative_minute})
        else:
            relative_minute = relative_minute + 1
            print(relative_minute)
            stickList[-1]['close'] = bid
            currentMin = dt_obj.minute
            stickList.append({'high':bid, 'low':bid, 'open':bid, 'minute':currentMin, 'relative_minute': relative_minute})

            #trend = ['nuetral', 0]
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

            #update cache every X minutes
            if(currentHour != dt_obj.hour):
                newHour()

def Onclose(ws):
    print('closed')

def getActiveMarkets():
    global currentKey

    time = datetime.now().hour
    if(crypto):
        return(markets["CRYPTO"])
    if(time>=17 and time < 19):
        currentKey = "AUS"
        return(markets["AUS"])
    if((time>=19)or(time<3)):
        currentKey = "ASI"
        return(markets["ASI"])
    if(time>=3 and time<8):
        currentKey = "EUR"
        return(markets["EUR"])
    if(time>=8 and time<17):
        currentKey = "USA"
        return(markets["USA"])


def main():
    global keys, currentMin, prevsticks
    keys = getActiveMarkets()
    if(crypto):
        address = 'wss://socket.polygon.io/crypto'
    else:
        address = 'wss://socket.polygon.io/forex'
    ws = websocket.WebSocketApp(address, on_open=Onopen, on_close=Onclose, on_message=on_message)
    ws.run_forever()

main()

