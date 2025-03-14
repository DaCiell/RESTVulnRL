from datetime import datetime

import redis as redis
from pymongo import MongoClient

from config import *


def redis_conn():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r.flushdb()
    return r


def mongo_conn():
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_NAME]
    return db


def mongo_insert(db, collection, endpoint_sequence):
    collection = db[collection]
    document_count = collection.count_documents({})
    id = document_count + 1
    results = {'id': id}
    for i in range(len(endpoint_sequence)):
        result = {}
        result['id'] = str(i + 1)
        result['path'] = endpoint_sequence[i].path
        result['method'] = endpoint_sequence[i].method
        result['url'] = endpoint_sequence[i].url
        result['headers'] = endpoint_sequence[i].headers
        result['body'] = endpoint_sequence[i].body
        result['category_dict'] = endpoint_sequence[i].category_dict
        result['val_dict'] = endpoint_sequence[i].val_dict
        results['endpoint' + str(i + 1)] = result
    collection.insert_one(results)


redis_conn = redis_conn()
mongo_conn = mongo_conn()
