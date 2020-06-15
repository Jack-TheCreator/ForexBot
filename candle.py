
class stick():
    def __init__(self, price, minute:int):
        self.open = price
        self.close = 0
        self.high = price
        self.low = price
        self.minute = minute

    def update(self, price):
        if(price > self.high):
            self.high = price
        if(price < self.low):
            self.low = price

