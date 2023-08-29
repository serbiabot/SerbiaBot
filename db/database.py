import json
import random

import redis


def redis_save(chat_id, data, renew=True):
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        if not renew:
            old = redis_get(chat_id)
            data = old + data
            random.shuffle(data)
        r.set(chat_id, json.dumps(data))
        r.close()
    except Exception as e:
        print(e)


def redis_clean(chat_id):
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        r.set(chat_id, '')
        r.close()
    except Exception as e:
        print(e)


def redis_get(chat_id):
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        retrieved_value = r.get(chat_id)
        r.close()
        return json.loads(retrieved_value.decode('utf-8'))
    except Exception as e:
        print(e)
