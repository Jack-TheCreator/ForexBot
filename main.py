import websocket
import orjson
import json
from dateutil.parser import parse
from datetime import datetime
from threading import Thread
#from candle import stick
import os

currentMin = -1
minstick = {}
hourstick = {}
tick = -1
prev = -1

markets = {"AUS":["C.NZD/USD","C.USD/AUD"],
           "ASI":["C.AUD/JPY","C.AUD/HKD"],
           "EUR":['C.JPY/EUR','C.HKD/GBP'],
           "USA":['C.EUR/USD','C.GBP/USD']}

def Onopen(ws):
    global keys
    print('OPEN++++++')
    auth = {
        "action": "auth",
        "params": os.environ.get("API_KEY")

    }
    ws.send(json.dumps(auth))
    ws.send(json.dumps({"action":"subscribe","params":keys[0]}))


def on_message(ws, message):
    global currentMin, minstick
    msg = orjson.loads(message)[0]
    if(msg['ev']=='status'):
        pass
    else:
        ask = msg['a']
        bid = msg['b']
        spread = ask - bid
        dt_obj = datetime.fromtimestamp(msg['t']/1000.0)
        if(currentMin == dt_obj.minute):
            if(bid<minstick[currentMin]['low']):
                minstick[currentMin]['low'] = bid
            elif(bid>minstick[currentMin]['high']):
                minstick[currentMin]['high'] = bid
        elif(currentMin == -1):
            currentMin = dt_obj.minute
            minstick[currentMin] = {'high':bid, 'low':bid, 'open':bid}
        else:
            minstick[currentMin]['close'] = bid
            currentMin = dt_obj.minute
            minstick[currentMin] = {'high':bid, 'low':bid, 'open':bid}


def Onclose(ws):
    print(minstick)
    print('closed')

def getActiveMarkets():
    time = datetime.now().hour

    if(time>=17 and time < 19):
        return(markets["AUS"])
    if((time>=19)or(time<3)):
        return(markets["ASI"])
    if(time>=3 and time<8):
        return(markets["EUR"])
    if(time>=8 and time<17):
        return(markets["USA"])


def main():
    global keys, currentMin, prevsticks
    keys = getActiveMarkets()
    address = 'wss://socket.polygon.io/forex'
    ws = websocket.WebSocketApp(address, on_open=Onopen, on_close=Onclose, on_message=on_message)
    ws.run_forever()

main()

