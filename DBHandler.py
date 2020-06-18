from abc import ABC
from redis import Redis
from typing import List
import pandas as pd
import numpy as np
import json
from datetime import datetime

class BaseHandler(ABC):
    def save_one(self, data:dict, key:str):
        raise NotImplementedError

    def save_many(self, data:list, key:str):
        raise NotImplementedError

    def load_latest(self, key:str) -> dict:
        raise NotImplementedError

    def get_latest_timestamp(self, key:str):
        raise NotImplementedError

    def load_hour(self, key:str):
        raise NotImplementedError

    def load_day(self, key:str):
        raise NotImplementedError

class Handler(BaseHandler):
    def __init__(self, redisConnection):
        self.redis = redisConnection

    def save_one(self, data:dict, key:str):
        saveable = {}
        saveable[data] = data['minute']
        self.redis.zadd(key, json.dumps(saveable))

    def save_many(self, data:list, key:str):
        saveable = {}
        for dt in data:
            saveable[dt] = dt['minute']
        self.redis.zadd(key, json.dumps(saveable))

    def load_latest(self, key:str) -> dict:
        jsonData = self.redis.zrevrange(key, 0, 0, withscores=False)
        return(json.loads(jsonData))

    def get_latest_timestamp(self, key:str):
        jsonData = self.redis.zrange(key, 0, 0, withscores=True)
        data = json.loads(jsonData)
        return data.values()

    def load_hour(self, key:str):
        jsonData = self.redis.zrange(key, 0, -1, withscores=False)
        return(json.loads(jsonData))

