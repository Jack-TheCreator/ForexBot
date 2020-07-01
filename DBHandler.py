from abc import ABC
from redis import Redis
from typing import List
import json
from datetime import datetime

class BaseHandler(ABC):
    def save_minutes(self, data:dict, key:str):
        raise NotImplementedError

    def save_minute(self, data:list, key:str):
        raise NotImplementedError

    def load_latest(self, key:str) -> dict:
        raise NotImplementedError

    def get_latest_timestamp(self, key:str):
        raise NotImplementedError

    def load_hour(self, key:str):
        raise NotImplementedError

    def load_day(self, key:str):
        raise NotImplementedError

    def load_all(self, key:str):
        raise NotImplementedError

class Handler(BaseHandler):
    def __init__(self, redisConnection):
        self.redis = redisConnection

    def save_minutes(self, data:dict, key:str):
        saveable = {}
        print(data)
        for dt in data:
            saveable[json.dumps(dt)] = dt['relative_minute']
        print(saveable)
        self.redis.zadd(key, saveable)
        return(True)

    def save_minute(self, data:list, key:str):
        saveable = {}
        saveable[json.dumps(data[0])] = data[0]['relative_minute']
        self.redis.zadd(key, saveable)

    def load_latest(self, key:str) -> dict:
        jsonData = self.redis.zrevrange(key, 0, 0, withscores=False)
        return(json.loads(jsonData))

    def get_latest_timestamp(self, key:str):
        jsonData = self.redis.zrange(key, 0, 0, withscores=True)
        data = json.loads(jsonData)
        return data.values()

    def load_hour(self, key:str):
        last = self.get_latest_timestamp(key)
        first = last - 60
        jsonData = self.redis.zrange(key, first, last, withscores=False)
        return(json.loads(jsonData))

    def load_all(self, key:str):
        data = []
        jsonData = self.redis.zrange(key, 0, -1, withscores=False)
        for dt in jsonData:
            data.append(json.loads(dt))
        return(data)